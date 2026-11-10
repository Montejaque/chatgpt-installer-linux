#!/usr/bin/env python3
"""Per-user graphical manager for the official OpenAI Codex CLI binary."""
import json, os, queue, shutil, subprocess, sys, tarfile, tempfile, threading, urllib.request, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_NAME = "Codex Installer & Updater"
REPO_API = "https://api.github.com/repos/openai/codex/releases/latest"
ASSET_NAME = "codex-x86_64-unknown-linux-musl.tar.gz"
CHATGPT_DEB_URL = "https://persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb"
HOME = Path.home()
LOCAL_OPT = HOME / ".local" / "opt"
INSTALL_DIR = LOCAL_OPT / "codex"
BIN_DIR = HOME / ".local" / "bin"
LAUNCHER = BIN_DIR / "codex"
DESKTOP_DIR = HOME / ".local" / "share" / "applications"
DESKTOP_FILE = DESKTOP_DIR / "codex.desktop"  # legacy manager-owned entry, removed and never recreated
CHATGPT_DESKTOP_FILE = DESKTOP_DIR / "chatgpt.desktop"
CHATGPT_APP_DIR = HOME / ".local" / "opt" / "chatgpt"
CHATGPT_LAUNCHER = BIN_DIR / "chatgpt-app"
CHATGPT_LAUNCHER_MARKER = "# managed-by: chatgpt-deb-installer-punto-vuela"
ICON_DIR = HOME / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
CHATGPT_ICON_SOURCE = HOME / ".local" / "opt" / "chatgpt" / "usr" / "lib" / "chatgpt" / "resources" / "icon-chatgpt.png"
CHATGPT_ICON = ICON_DIR / "codex-chatgpt.png"
BUNDLED_CHATGPT_CODEX = HOME / ".local" / "opt" / "chatgpt" / "usr" / "lib" / "chatgpt" / "resources" / "codex"
VERSION_FILE = INSTALL_DIR / ".managed-version"
USER_AGENT = "Codex-Installer-Updater-Punto-Vuela-Montejaque"
LAUNCHER_MARKER = "# managed-by: codex-installer-punto-vuela"
DESKTOP_MARKER = "X-Codex-Installer-Managed=true"

def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def select_linux_asset(release):
    for asset in release.get("assets", []):
        if asset.get("name") == ASSET_NAME:
            url = asset.get("browser_download_url", "")
            if url.startswith("https://github.com/openai/codex/releases/download/"):
                return asset
    raise RuntimeError("La publicación oficial no contiene el archivo Linux x86_64 esperado.")

def safe_binary_member(archive):
    expected = "codex-x86_64-unknown-linux-musl"
    matches = [m for m in archive.getmembers() if m.isfile() and Path(m.name).name == expected]
    if len(matches) != 1:
        raise RuntimeError("El archivo oficial no contiene un ejecutable Codex válido.")
    return matches[0]

def latest_release():
    data = http_json(REPO_API)
    asset = select_linux_asset(data)
    tag = data.get("tag_name", "").strip()
    if not tag:
        raise RuntimeError("La publicación oficial no indica una versión.")
    return tag, asset

def runtime_environment(extra_bin=None):
    """Build a GUI-safe PATH including per-user Node/NVM package locations."""
    entries = []
    if extra_bin:
        entries.append(str(extra_bin))
    entries.extend([
        str(BIN_DIR),
        str(HOME / ".npm-global" / "bin"),
        str(HOME / ".local" / "share" / "npm" / "bin"),
        str(HOME / ".npm" / "bin"),
        str(HOME / ".bun" / "bin"),
        str(HOME / ".volta" / "bin"),
        str(HOME / ".asdf" / "shims"),
    ])
    nvm_root = HOME / ".nvm" / "versions" / "node"
    if nvm_root.is_dir():
        entries.extend(str(p) for p in sorted(nvm_root.glob("*/bin"), reverse=True))
    existing = os.environ.get("PATH", "").split(os.pathsep)
    return os.pathsep.join(dict.fromkeys([p for p in entries + existing if p]))

def run_codex_version(binary):
    binary = Path(binary).expanduser()
    env = os.environ.copy()
    env["PATH"] = runtime_environment(binary.parent)
    result = subprocess.run([str(binary), "--version"], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, universal_newlines=True, timeout=30, env=env)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() or "No se pudo ejecutar Codex.")
    output = result.stdout.strip().splitlines()
    if not output:
        raise RuntimeError("Codex no devolvió información de versión.")
    return output[0]

def find_codex_executable():
    """Find the user's existing Codex CLI without requiring a login-shell PATH."""
    candidates = [INSTALL_DIR / "codex", BIN_DIR / "codex", BUNDLED_CHATGPT_CODEX]
    path_env = runtime_environment()
    path_hit = shutil.which("codex", path=path_env)
    if path_hit:
        candidates.append(Path(path_hit))
    candidates.extend([
        HOME / ".npm-global" / "bin" / "codex",
        HOME / ".local" / "share" / "npm" / "bin" / "codex",
        HOME / ".npm" / "bin" / "codex",
        HOME / ".bun" / "bin" / "codex",
        HOME / ".volta" / "bin" / "codex",
        HOME / ".asdf" / "shims" / "codex",
        HOME / "bin" / "codex",
        Path("/usr/local/bin/codex"),
        Path("/usr/bin/codex"),
    ])
    nvm_root = HOME / ".nvm" / "versions" / "node"
    if nvm_root.is_dir():
        for node_bin in sorted(nvm_root.glob("*/bin"), reverse=True):
            candidates.append(node_bin / "codex")
    seen = set()
    for candidate in candidates:
        try:
            # Keep the original path: executing a resolved npm symlink can bypass
            # its shebang or package shim and fail to locate the Node runtime.
            path = candidate.expanduser()
            key = str(path.absolute())
            if key in seen:
                continue
            seen.add(key)
            if path.is_file() and os.access(str(path), os.X_OK):
                return path
        except OSError:
            continue
    return None

def installed_details():
    """Return (version, executable path), including per-user installations."""
    binary = find_codex_executable()
    if binary is None:
        if INSTALL_DIR.exists():
            return "Instalación incompleta", str(INSTALL_DIR / "codex")
        return None, None
    try:
        return run_codex_version(binary), str(binary)
    except Exception as exc:
        return "No se pudo consultar la versión (" + str(exc) + ")", str(binary)

def installed_version():
    return installed_details()[0]

def installed_release_tag():
    """Return the release tag recorded by this manager, if available."""
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None

def is_managed_file(path, marker):
    try:
        return path.is_file() and marker in path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False

def check_access_conflicts():
    if (LAUNCHER.exists() or LAUNCHER.is_symlink()) and not is_managed_file(LAUNCHER, LAUNCHER_MARKER):
        raise RuntimeError("Ya existe ~/.local/bin/codex y no pertenece a este gestor. No se sobrescribirá.")

def ensure_chatgpt_menu_entry(log=None):
    """Preserve the graphical ChatGPT launcher, restoring its shipped entry only if missing."""
    log = log or (lambda value: None)
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    if CHATGPT_DESKTOP_FILE.is_file():
        log("Se conserva el acceso gráfico ChatGPT existente.")
        return str(CHATGPT_DESKTOP_FILE)
    if CHATGPT_APP_DIR.is_dir():
        for candidate in CHATGPT_APP_DIR.rglob("*.desktop"):
            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
                names = [line.strip().lower() for line in content.splitlines()]
                if "[Desktop Entry]" in content and ("name=chatgpt" in names or "name=openai chatgpt" in names):
                    shutil.copy2(str(candidate), str(CHATGPT_DESKTOP_FILE))
                    log("Se ha restaurado el acceso gráfico ChatGPT desde la instalación existente.")
                    return str(CHATGPT_DESKTOP_FILE)
            except OSError:
                continue
    log("No se encontró el acceso gráfico ChatGPT original. No se creará un acceso Codex CLI en el menú.")
    return None

def write_access_files():
    if not (INSTALL_DIR / "codex").is_file():
        raise RuntimeError("No se encuentra Codex. Instala o actualiza primero.")
    check_access_conflicts()
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    # Keep the CLI command available in the terminal, but never create a GUI menu item for it.
    LAUNCHER.write_text('#!/bin/sh\n' + LAUNCHER_MARKER + '\nexec "$HOME/.local/opt/codex/codex" "$@"\n', encoding="utf-8")
    LAUNCHER.chmod(0o755)
    # Remove only the legacy menu entry created by older versions of this manager.
    if is_managed_file(DESKTOP_FILE, DESKTOP_MARKER):
        DESKTOP_FILE.unlink()
    ensure_chatgpt_menu_entry()



def find_chatgpt_binary(rootfs):
    candidates = [rootfs / "usr" / "bin" / "chatgpt",
                  rootfs / "usr" / "lib" / "chatgpt" / "chatgpt",
                  rootfs / "opt" / "chatgpt" / "chatgpt"]
    for candidate in candidates:
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return candidate
    raise RuntimeError("El DEB no contiene el ejecutable gráfico ChatGPT esperado.")

def install_chatgpt_desktop_entry(binary):
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    app_home = CHATGPT_APP_DIR / "usr" / "lib" / "chatgpt"
    CHATGPT_LAUNCHER.write_text(
        '#!/bin/sh\n' + CHATGPT_LAUNCHER_MARKER + '\n'
        + 'cd "' + str(app_home) + '" || exit 1\n'
        + 'exec "' + str(binary) + '" "$@"\n', encoding="utf-8")
    CHATGPT_LAUNCHER.chmod(0o755)
    icon_candidates = [app_home / "resources" / "icon-chatgpt.png",
        CHATGPT_APP_DIR / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "chatgpt.png",
        CHATGPT_APP_DIR / "usr" / "share" / "pixmaps" / "chatgpt.png"]
    icon = next((p for p in icon_candidates if p.is_file()), None)
    desktop = ("[Desktop Entry]\nVersion=1.0\nType=Application\nName=ChatGPT\n"
        "GenericName=ChatGPT\nComment=Aplicación gráfica de ChatGPT\n"
        "Exec=" + str(CHATGPT_LAUNCHER) + " %U\n"
        "Icon=" + (str(icon) if icon else "chatgpt") + "\n"
        "Terminal=false\nCategories=Development;IDE;Utility;\nStartupNotify=true\n"
        "X-Punto-Vuela-Managed=true\n")
    CHATGPT_DESKTOP_FILE.write_text(desktop, encoding="utf-8")
    CHATGPT_DESKTOP_FILE.chmod(0o644)

def install_or_update_chatgpt(progress=None, log=None):
    progress = progress or (lambda value: None)
    log = log or (lambda value: None)
    LOCAL_OPT.mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix="chatgpt-deb-", dir=str(LOCAL_OPT)))
    deb_path, extracted = temp_root / "chatgpt_amd64.deb", temp_root / "rootfs"
    extracted.mkdir()
    backup = temp_root / "previous-chatgpt"
    try:
        log("Descargando el paquete DEB oficial de ChatGPT…")
        request = urllib.request.Request(CHATGPT_DEB_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=180) as response, deb_path.open("wb") as output:
            total = int(response.headers.get("Content-Length", "0") or 0)
            received = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                received += len(chunk)
                if total:
                    progress(min(45, 5 + int(40 * received / total)))
        if deb_path.stat().st_size < 1024 * 1024:
            raise RuntimeError("La descarga del DEB está incompleta o no es válida.")
        log("Extrayendo ChatGPT sin permisos de administrador…")
        subprocess.run(["dpkg-deb", "-x", str(deb_path), str(extracted)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=180)
        find_chatgpt_binary(extracted)
        progress(70)
        if CHATGPT_APP_DIR.exists():
            os.replace(str(CHATGPT_APP_DIR), str(backup))
        try:
            os.replace(str(extracted), str(CHATGPT_APP_DIR))
            installed_binary = find_chatgpt_binary(CHATGPT_APP_DIR)
            install_chatgpt_desktop_entry(installed_binary)
        except Exception:
            if CHATGPT_APP_DIR.exists():
                shutil.rmtree(CHATGPT_APP_DIR, ignore_errors=True)
            if backup.exists():
                os.replace(str(backup), str(CHATGPT_APP_DIR))
            raise
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        progress(100)
        log("ChatGPT gráfico instalado/actualizado desde el DEB oficial.")
        log("Acceso del menú creado: " + str(CHATGPT_DESKTOP_FILE))
        return str(CHATGPT_APP_DIR)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def install_or_update(progress=None, log=None):
    progress = progress or (lambda value: None)
    log = log or (lambda value: None)
    check_access_conflicts()
    LOCAL_OPT.mkdir(parents=True, exist_ok=True)
    tag, asset = latest_release()
    log("Última versión oficial: " + tag)
    temp_root = Path(tempfile.mkdtemp(prefix="codex-installer-", dir=str(LOCAL_OPT)))
    staging, archive_path = temp_root / "codex", temp_root / "codex.tar.gz"
    staging.mkdir()
    try:
        log("Descargando el ejecutable oficial de OpenAI…")
        req = urllib.request.Request(asset["browser_download_url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as response, archive_path.open("wb") as output:
            total = int(response.headers.get("Content-Length", "0") or 0)
            received = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                received += len(chunk)
                if total:
                    progress(min(65, 10 + int(55 * received / total)))
        if archive_path.stat().st_size < 1024 * 1024:
            raise RuntimeError("La descarga es demasiado pequeña; se cancela la instalación.")
        log("Comprobando y extrayendo el archivo…")
        with tarfile.open(str(archive_path), "r:gz") as archive:
            member = safe_binary_member(archive)
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError("No se pudo leer el ejecutable descargado.")
            with source, (staging / "codex").open("wb") as output:
                shutil.copyfileobj(source, output)
        (staging / ".managed-version").write_text(tag + "\n", encoding="utf-8")
        binary = staging / "codex"
        binary.chmod(0o755)
        log("Verificando el ejecutable descargado…")
        log("Ejecutable verificado: " + run_codex_version(binary))
        progress(82)
        # Non-destructive update: keep the existing installation directory and
        # every user-added file in it. Only replace the Codex executable and
        # this manager's own version marker, after the new binary is verified.
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        version_tmp = INSTALL_DIR / ".managed-version.tmp"
        version_tmp.write_text(tag + "\n", encoding="utf-8")
        os.replace(str(binary), str(INSTALL_DIR / "codex"))
        os.replace(str(version_tmp), str(VERSION_FILE))
        write_access_files()
        progress(100)
        log("Instalación completada. Se conserva la configuración de ~/.codex.")
        return tag
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

def repair_access():
    write_access_files()
    return "Comando de terminal reparado. El acceso gráfico ChatGPT se conserva; no se crea un acceso Codex CLI en el menú."

def uninstall_managed():
    removed = []
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
        removed.append(str(INSTALL_DIR))
    for path, marker in ((LAUNCHER, LAUNCHER_MARKER), (DESKTOP_FILE, DESKTOP_MARKER)):
        if is_managed_file(path, marker):
            path.unlink()
            removed.append(str(path))
    # Keep the graphical ChatGPT launcher and its original icon untouched.
    return removed

class ManagerApp:
    """Interfaz alineada con VS Code Installer & Updater de Punto Vuela."""
    def __init__(self, root):
        self.root = root
        root.title("Codex Installer & Updater — Punto Vuela Montejaque")
        root.geometry("775x610")
        root.minsize(700, 560)
        root.configure(bg="white")
        self.events = queue.Queue()
        self.busy = False
        self.build()
        self.refresh_status()
        root.after(120, self.poll)

    def build(self):
        outer = tk.Frame(self.root, bg="white", padx=22, pady=18)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="Codex Installer & Updater", bg="white", fg="black",
                 font=("DejaVu Sans", 21, "bold")).pack(anchor="w")
        tk.Label(outer, text="Linux x64 · Sin root · Punto Vuela Montejaque",
                 bg="white", fg="#222222", font=("DejaVu Sans", 9)).pack(anchor="w", pady=(3, 15))

        tk.Frame(outer, bg="#F3D54E", height=4).pack(fill="x", pady=(0, 20))

        self.status_label = tk.Label(outer, text="Comprobando instalación de Codex…",
            bg="white", fg="black", font=("DejaVu Sans", 9), anchor="w")
        self.status_label.pack(fill="x", pady=(0, 16))
        self.detail_label = tk.Label(outer, text="", bg="white", fg="#333333",
            font=("DejaVu Sans", 8), anchor="w")
        self.detail_label.pack(fill="x", pady=(0, 14))

        actions = tk.Frame(outer, bg="white")
        actions.pack(fill="x", pady=(0, 12))
        self.install_btn = self.button(actions, "Instalar / actualizar Codex", self.do_install)
        self.chatgpt_btn = self.button(actions, "Instalar / actualizar ChatGPT", self.do_install_chatgpt)
        self.check_btn = self.button(actions, "Comprobar versión", self.do_check)
        self.repair_btn = self.button(actions, "Reparar acceso", self.do_repair)
        self.remove_btn = self.button(actions, "Desinstalar y eliminar datos", self.do_uninstall)
        for i, btn in enumerate((self.install_btn, self.chatgpt_btn, self.check_btn, self.repair_btn, self.remove_btn)):
            btn.pack(side="left", padx=(0 if i == 0 else 8, 0), fill="x", expand=True)

        self.progress_label = tk.Label(outer, text="Preparado", bg="white", fg="#222222",
            font=("DejaVu Sans", 8), anchor="w")
        self.progress_label.pack(fill="x", pady=(0, 4))
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Codex.Horizontal.TProgressbar", troughcolor="#D8D6D0",
                        background="#B7B3A9", bordercolor="#B7B3A9", lightcolor="#B7B3A9",
                        darkcolor="#B7B3A9")
        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100,
                                        style="Codex.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 8))

        self.log_box = tk.Text(outer, height=12, bg="#FAFAFA", fg="black",
            insertbackground="black", relief="solid", bd=1, wrap="word",
            font=("DejaVu Sans Mono", 8), padx=3, pady=3)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

        footer = tk.Frame(outer, bg="white")
        footer.pack(fill="x", pady=(10, 0))
        contact = tk.Frame(footer, bg="white")
        contact.pack(side="left", fill="x", expand=True)
        tk.Label(contact, text="Desarrollador: Francisco Javier Gallego Orellana",
            bg="white", fg="black", font=("DejaVu Sans", 8, "bold")).pack(anchor="w")
        tk.Label(contact, text="Punto Vuela Montejaque · Avenida Andalucía, 48 · 29360 Montejaque (Málaga)",
            bg="white", fg="#222222", font=("DejaVu Sans", 8)).pack(anchor="w", pady=(2, 0))
        tk.Label(contact, text="Teléfono: 633 402 959 · Correo: montejaque@puntosvuela.es",
            bg="white", fg="#222222", font=("DejaVu Sans", 8)).pack(anchor="w")
        self.guide_btn = tk.Button(footer, text="Ver guía de uso", command=self.open_guide,
            relief="raised", bd=1, font=("DejaVu Sans", 8), padx=8, pady=5)
        self.guide_btn.pack(side="right", anchor="s", padx=(8, 0), pady=(35, 0))

    def button(self, parent, label, command):
        return tk.Button(parent, text=label, command=command, relief="raised", bd=1,
            font=("DejaVu Sans", 8), padx=7, pady=5, cursor="hand2")

    def open_guide(self):
        filename = "Guia-Codex-Installer-Puntos-Vuela-Montejaque.pdf"
        destination = HOME / ".local" / "share" / "doc" / "codex-installer" / filename
        bundled = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / filename
        candidates = [bundled, destination]
        source = next((item for item in candidates if item.is_file()), None)
        try:
            if source is None:
                raise FileNotFoundError("No se ha encontrado la guía PDF incluida en la aplicación.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != destination.resolve():
                shutil.copy2(str(source), str(destination))
            subprocess.Popen(["xdg-open", str(destination)], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir la guía", str(exc) +
                "\\n\\nPuedes descargarla desde la página de versiones de GitHub.", parent=self.root)
            webbrowser.open("https://github.com/Montejaque/chatgpt-installer-linux/releases/latest")

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def refresh_status(self):
        """Refresh detected installation without blocking Tk's main event loop."""
        self.status_label.configure(text="Comprobando instalación de Codex…")
        self.detail_label.configure(text="Consultando el ejecutable detectado…")
        def worker():
            try:
                current, executable = installed_details()
                self.events.put(("detected_status", (current, executable)))
            except Exception as exc:
                self.events.put(("detected_status_error", str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def start(self, action):
        if self.busy:
            return
        self.busy = True
        self.progress["value"] = 0
        self.progress_label.configure(text="En curso…")
        for button in (self.install_btn, self.chatgpt_btn, self.check_btn, self.repair_btn, self.remove_btn):
            button.configure(state="disabled")
        def worker():
            try:
                action()
            except Exception as exc:
                self.events.put(("error", str(exc)))
            finally:
                self.events.put(("done", None))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            while True:
                item = self.events.get_nowait()
                if not isinstance(item, tuple) or len(item) != 2:
                    self.log("Aviso: se ha descartado un evento interno no válido.")
                    continue
                kind, value = item
                if kind == "log":
                    self.log(value)
                elif kind == "progress":
                    self.progress["value"] = value
                elif kind == "status":
                    self.status_label.configure(text=value)
                elif kind == "detail":
                    self.detail_label.configure(text=value)
                elif kind == "detected_status":
                    current, executable = value
                    if current:
                        self.status_label.configure(text="Versión instalada: " + current)
                        self.detail_label.configure(text="Ejecutable detectado: " + str(executable))
                    else:
                        self.status_label.configure(text="Versión instalada: No instalada")
                        self.detail_label.configure(text="No se ha encontrado el comando codex en las rutas habituales ni en PATH.")
                elif kind == "detected_status_error":
                    self.status_label.configure(text="No se pudo comprobar la instalación")
                    self.detail_label.configure(text=value)
                    self.log("ERROR al comprobar instalación: " + value)
                elif kind == "progress_text":
                    self.progress_label.configure(text=value)
                elif kind == "error":
                    self.log("ERROR: " + value)
                    self.progress_label.configure(text="Operación no completada")
                    messagebox.showerror("No se pudo completar la operación", value, parent=self.root)
                elif kind == "done":
                    self.busy = False
                    for button in (self.install_btn, self.check_btn, self.repair_btn, self.remove_btn):
                        button.configure(state="normal")
                    if self.progress["value"] >= 100:
                        self.progress_label.configure(text="Completado")
                    elif self.progress_label.cget("text") == "En curso…":
                        self.progress_label.configure(text="Preparado")
                    # Never run codex --version on Tk's main thread.
                    self.refresh_status()
        except queue.Empty:
            pass
        except Exception as exc:
            # A malformed UI event must never stop the Tk event pump.
            try:
                self.log("ERROR interno de interfaz: " + str(exc))
                self.progress_label.configure(text="Error interno; revisa el registro")
            except Exception:
                pass
        finally:
            if self.root.winfo_exists():
                self.root.after(120, self.poll)

    def do_install(self):
        def action():
            self.events.put(("log", "Instalando o actualizando Codex CLI desde la publicación oficial de OpenAI…"))
            tag = install_or_update(lambda n: self.events.put(("progress", n)),
                                    lambda s: self.events.put(("log", s)))
            self.events.put(("progress", 100))
            self.events.put(("progress_text", "Instalación completada"))
            self.events.put(("status", "Codex instalado: " + tag))
            self.events.put(("log", "Resultado: instalación completada correctamente."))
        self.start(action)

    def do_install_chatgpt(self):
        def action():
            self.events.put(("log", "Instalando la aplicación gráfica ChatGPT desde el DEB oficial…"))
            install_or_update_chatgpt(
                lambda n: self.events.put(("progress", n)),
                lambda message: self.events.put(("log", message)))
            self.events.put(("progress_text", "ChatGPT instalado correctamente"))
            self.events.put(("status", "Aplicación gráfica ChatGPT instalada"))
        self.start(action)

    def do_check(self):
        def action():
            self.events.put(("log", "Comprobando instalaciones de Codex…"))
            current, executable = installed_details()
            self.events.put(("log", "Versión instalada: " + (current or "No instalada")))
            if executable:
                self.events.put(("log", "Ejecutable detectado: " + executable))
            if current and current != "Instalación dañada" and current != "Instalación incompleta":
                try:
                    tag, asset = latest_release()
                    self.events.put(("log", "Última versión oficial disponible: " + tag))
                    self.events.put(("detail", "Ejecutable detectado: " + str(executable or INSTALL_DIR / "codex")))
                    installed_tag = installed_release_tag()
                    up_to_date = (installed_tag == tag) if installed_tag else (current == tag or current.endswith(tag.lstrip("v")))
                    status_text = ("Codex está actualizado · Versión instalada: " + current
                                   if up_to_date else
                                   "Hay una actualización disponible · Versión instalada: " + current)
                    self.events.put(("status", status_text))
                    self.events.put(("log", "Fuente: github.com/openai/codex · " + asset["name"]))
                except Exception as exc:
                    self.events.put(("log", "No se pudo consultar la versión remota: " + str(exc)))
            else:
                tag, asset = latest_release()
                self.events.put(("log", "Última versión oficial disponible: " + tag))
                self.events.put(("detail", "Fuente oficial: github.com/openai/codex"))
            self.events.put(("progress", 100))
        self.start(action)

    def do_repair(self):
        def action():
            self.events.put(("log", "Reparando accesos de Codex…"))
            self.events.put(("log", repair_access()))
            self.events.put(("progress", 100))
        self.start(action)

    def do_uninstall(self):
        if not messagebox.askyesno("Confirmar desinstalación",
            "Se eliminarán la aplicación Codex CLI gestionada por este instalador y sus accesos directos.\n\n"
            "Se conservarán ~/.codex, credenciales, sesiones y configuración personal.",
            parent=self.root):
            return
        def action():
            self.events.put(("log", "Desinstalando la copia gestionada de Codex…"))
            removed = uninstall_managed()
            self.events.put(("log", "Desinstalación completada."))
            for item in removed:
                self.events.put(("log", "Eliminado: " + item))
            self.events.put(("log", "Se ha conservado ~/.codex y todos sus datos personales."))
            self.events.put(("progress", 100))
        self.start(action)

def main():
    if "--self-test" in sys.argv:
        try:
            tk.Tcl()
        except Exception as exc:
            print("Tkinter self-test failed: " + str(exc), file=sys.stderr)
            return 1
        print("Codex Installer & Updater: self-test OK")
        return 0
    if "--version" in sys.argv:
        print("Codex Installer & Updater 1.0.0")
        return 0
    root = tk.Tk()
    ManagerApp(root)
    root.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(main())
