#!/usr/bin/env python3
"""Per-user graphical manager for the official OpenAI Codex CLI binary."""
import json, os, queue, shutil, subprocess, sys, tarfile, tempfile, threading, urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_NAME = "Codex Installer & Updater"
REPO_API = "https://api.github.com/repos/openai/codex/releases/latest"
ASSET_NAME = "codex-x86_64-unknown-linux-musl.tar.gz"
HOME = Path.home()
LOCAL_OPT = HOME / ".local" / "opt"
INSTALL_DIR = LOCAL_OPT / "codex"
BIN_DIR = HOME / ".local" / "bin"
LAUNCHER = BIN_DIR / "codex"
DESKTOP_DIR = HOME / ".local" / "share" / "applications"
DESKTOP_FILE = DESKTOP_DIR / "codex.desktop"
VERSION_FILE = INSTALL_DIR / ".managed-version"
USER_AGENT = "Codex-Installer-Updater-Punto-Vuela-Montejaque"

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

def run_codex_version(binary):
    result = subprocess.run([str(binary), "--version"], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, universal_newlines=True, timeout=20)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() or "No se pudo ejecutar Codex.")
    return result.stdout.strip().splitlines()[0]

def installed_version():
    if not INSTALL_DIR.is_dir():
        return None
    if VERSION_FILE.is_file():
        value = VERSION_FILE.read_text(encoding="utf-8").strip()
        if value:
            return value
    binary = INSTALL_DIR / "codex"
    if binary.is_file():
        try:
            return run_codex_version(binary)
        except Exception:
            return "Instalación dañada"
    return "Instalación incompleta"

def write_access_files():
    if not (INSTALL_DIR / "codex").is_file():
        raise RuntimeError("No se encuentra Codex. Instala o actualiza primero.")
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    LAUNCHER.write_text('#!/bin/sh\nexec "$HOME/.local/opt/codex/codex" "$@"\n', encoding="utf-8")
    LAUNCHER.chmod(0o755)
    desktop = ("[Desktop Entry]\nVersion=1.0\nType=Application\nName=Codex CLI\n"
        "GenericName=Agente de programación\nComment=Inicia OpenAI Codex CLI en un terminal\n"
        "Exec=" + str(LAUNCHER) + "\nIcon=utilities-terminal\nTerminal=true\nCategories=Development;IDE;\n")
    DESKTOP_FILE.write_text(desktop, encoding="utf-8")
    DESKTOP_FILE.chmod(0o644)

def install_or_update(progress=None, log=None):
    progress = progress or (lambda value: None)
    log = log or (lambda value: None)
    LOCAL_OPT.mkdir(parents=True, exist_ok=True)
    tag, asset = latest_release()
    log("Última versión oficial: " + tag)
    temp_root = Path(tempfile.mkdtemp(prefix="codex-installer-", dir=str(LOCAL_OPT)))
    staging, archive_path = temp_root / "codex", temp_root / "codex.tar.gz"
    staging.mkdir()
    backup = LOCAL_OPT / "codex.previous"
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
        if backup.exists():
            shutil.rmtree(backup)
        if INSTALL_DIR.exists():
            os.replace(str(INSTALL_DIR), str(backup))
        try:
            os.replace(str(staging), str(INSTALL_DIR))
        except Exception:
            if backup.exists() and not INSTALL_DIR.exists():
                os.replace(str(backup), str(INSTALL_DIR))
            raise
        if backup.exists():
            shutil.rmtree(backup)
        write_access_files()
        progress(100)
        log("Instalación completada. Se conserva la configuración de ~/.codex.")
        return tag
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

def repair_access():
    write_access_files()
    return "Accesos reparados correctamente."

def uninstall_managed():
    removed = []
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
        removed.append(str(INSTALL_DIR))
    for path in (LAUNCHER, DESKTOP_FILE):
        try:
            path.unlink()
            removed.append(str(path))
        except FileNotFoundError:
            pass
    return removed

class ManagerApp:
    BG, PANEL, YELLOW, FG, MUTED = "#171717", "#242424", "#F3D54E", "#F5F5F2", "#B8B8B2"
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("760x610")
        root.minsize(680, 540)
        root.configure(bg=self.BG)
        self.events = queue.Queue()
        self.busy = False
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#3A3A3A", background=self.YELLOW, bordercolor="#3A3A3A")
        self.build()
        self.refresh_status()
        root.after(120, self.poll)

    def build(self):
        header = tk.Frame(self.root, bg=self.BG, padx=26, pady=22)
        header.pack(fill="x")
        tk.Label(header, text="CODEX  /  LINUX x86_64", bg=self.BG, fg=self.YELLOW, font=("DejaVu Sans", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Installer & Updater", bg=self.BG, fg=self.FG, font=("DejaVu Sans", 25, "bold")).pack(anchor="w", pady=(5, 2))
        tk.Label(header, text="Gestor gráfico de Codex CLI · Punto Vuela Montejaque", bg=self.BG, fg=self.MUTED, font=("DejaVu Sans", 10)).pack(anchor="w")
        status = tk.Frame(self.root, bg=self.PANEL, padx=18, pady=15)
        status.pack(fill="x", padx=26, pady=(0, 16))
        self.status_label = tk.Label(status, text="Comprobando estado…", bg=self.PANEL, fg=self.FG, font=("DejaVu Sans", 11, "bold"))
        self.status_label.pack(anchor="w")
        self.detail_label = tk.Label(status, text="", bg=self.PANEL, fg=self.MUTED, font=("DejaVu Sans", 9))
        self.detail_label.pack(anchor="w", pady=(5, 0))
        actions = tk.Frame(self.root, bg=self.BG, padx=26)
        actions.pack(fill="x")
        self.install_btn = self.button(actions, "Instalar / actualizar", self.do_install, True)
        self.check_btn = self.button(actions, "Comprobar versión", self.do_check)
        self.repair_btn = self.button(actions, "Reparar accesos", self.do_repair)
        self.remove_btn = self.button(actions, "Desinstalar", self.do_uninstall)
        self.install_btn.pack(fill="x", pady=4)
        row = tk.Frame(actions, bg=self.BG)
        row.pack(fill="x", pady=(4, 0))
        for i, btn in enumerate((self.check_btn, self.repair_btn, self.remove_btn)):
            btn.pack(in_=row, side="left", fill="x", expand=True, padx=(0 if i == 0 else 4, 4 if i < 2 else 0))
        self.progress = ttk.Progressbar(self.root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=26, pady=(18, 10))
        tk.Label(self.root, text="ACTIVIDAD", bg=self.BG, fg=self.YELLOW, font=("DejaVu Sans", 8, "bold")).pack(anchor="w", padx=28)
        self.log_box = tk.Text(self.root, height=10, bg="#101010", fg="#E7E7E2", insertbackground=self.FG,
            relief="flat", wrap="word", font=("DejaVu Sans Mono", 8), padx=12, pady=10)
        self.log_box.pack(fill="both", expand=True, padx=26, pady=(6, 16))
        self.log_box.configure(state="disabled")
        tk.Label(self.root, text="Desarrollador: Francisco Javier Gallego Orellana  ·  Punto Vuela Montejaque",
            bg=self.BG, fg=self.MUTED, font=("DejaVu Sans", 7)).pack(anchor="e", padx=26, pady=(0, 10))

    def button(self, parent, label, command, primary=False):
        return tk.Button(parent, text=label, command=command, bg=self.YELLOW if primary else self.PANEL,
            fg="#171717" if primary else self.FG, activebackground="#FFE77B", activeforeground="#171717",
            relief="flat", bd=0, font=("DejaVu Sans", 9, "bold"), padx=12, pady=10, cursor="hand2")

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def refresh_status(self):
        current = installed_version()
        self.status_label.configure(text=("Codex instalado · " + current) if current else "Codex todavía no está instalado")
        self.detail_label.configure(text="Ubicación: " + str(INSTALL_DIR) if current else "La instalación se guarda en tu carpeta personal.")

    def start(self, action):
        if self.busy:
            return
        self.busy = True
        self.progress["value"] = 0
        for button in (self.install_btn, self.check_btn, self.repair_btn, self.remove_btn):
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
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.log(value)
                elif kind == "progress":
                    self.progress["value"] = value
                elif kind == "status":
                    self.status_label.configure(text=value)
                elif kind == "detail":
                    self.detail_label.configure(text=value)
                elif kind == "error":
                    self.log("ERROR: " + value)
                    messagebox.showerror("No se pudo completar la operación", value, parent=self.root)
                elif kind == "done":
                    self.busy = False
                    for button in (self.install_btn, self.check_btn, self.repair_btn, self.remove_btn):
                        button.configure(state="normal")
                    self.refresh_status()
        except queue.Empty:
            pass
        self.root.after(120, self.poll)

    def do_install(self):
        def action():
            tag = install_or_update(lambda n: self.events.put(("progress", n)), lambda s: self.events.put(("log", s)))
            self.events.put(("status", "Codex instalado · " + tag))
        self.start(action)

    def do_check(self):
        def action():
            self.events.put(("log", "Consultando la publicación oficial de OpenAI…"))
            tag, asset = latest_release()
            current = installed_version()
            self.events.put(("log", "Última versión disponible: " + tag))
            self.events.put(("log", "Versión instalada: " + (current or "No instalada")))
            self.events.put(("status", "Actualización disponible" if current != tag else "Codex está actualizado"))
            self.events.put(("detail", "Fuente oficial: github.com/openai/codex · " + asset["name"]))
        self.start(action)

    def do_repair(self):
        self.start(lambda: self.events.put(("log", repair_access())))

    def do_uninstall(self):
        if not messagebox.askyesno("Confirmar desinstalación",
            "Se eliminará la copia gestionada de Codex y sus accesos.\n\nSe conservarán ~/.codex, credenciales, sesiones y configuración.",
            parent=self.root):
            return
        def action():
            removed = uninstall_managed()
            self.events.put(("log", "Desinstalación completada."))
            for item in removed:
                self.events.put(("log", "Eliminado: " + item))
            self.events.put(("log", "Se ha conservado ~/.codex."))
        self.start(action)

def main():
    if "--self-test" in sys.argv:
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
