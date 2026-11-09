# ChatGPT & Codex Installer — Punto Vuela Montejaque

Gestor gráfico para descargar, extraer, instalar por usuario, actualizar, comprobar y reparar el acceso a la aplicación oficial ChatGPT para Linux (incluye Codex).

**No requiere root, sudo, APT ni instalación en directorios del sistema.** Extrae el `.deb` oficial con `dpkg-deb -x` dentro de `~/.local/opt/chatgpt`; no ejecuta `dpkg -i` ni instala dependencias del sistema.

> **Compatibilidad:** OpenAI indica soporte oficial para Ubuntu 24.04/26.04, Debian 13, Fedora 43/44 y Arch actual. Ubuntu 20.04 no está soportado oficialmente. El gestor puede probarse allí, pero no garantiza que la aplicación arranque.

## Descargar

- [Última versión y AppImage](https://github.com/Montejaque/chatgpt-installer-linux/releases/latest)
- [Todas las versiones](https://github.com/Montejaque/chatgpt-installer-linux/releases)
- [GitHub Actions](https://github.com/Montejaque/chatgpt-installer-linux/actions)

Descarga `ChatGPT-Installer-x86_64.AppImage`, dale permiso de ejecución y ábrelo:

```bash
chmod +x ChatGPT-Installer-x86_64.AppImage
./ChatGPT-Installer-x86_64.AppImage
```

El AppImage es el gestor, no contiene la aplicación ChatGPT. El gestor descarga el paquete oficial cuando se pulsa **Instalar / actualizar**.

## Funciones

- Descarga el `.deb` x64 desde el endpoint oficial de OpenAI.
- Comprueba el nombre del paquete, arquitectura y versión declarada.
- Extrae el paquete sin root con `dpkg-deb -x`.
- Instala en `~/.local/opt/chatgpt`.
- Copia el icono oficial del paquete a `~/.local/share/icons/hicolor/256x256/apps/chatgpt.png`.
- Crea el acceso GNOME `~/.local/share/applications/chatgpt.desktop` en la categoría `Development;IDE;` (Programación).
- Crea el comando `~/.local/bin/chatgpt`.
- Comprueba la instalación y repara los accesos.
- Desinstala los archivos gestionados sin borrar preferencias ni datos personales.

## Rutas

| Elemento | Ruta |
|---|---|
| Aplicación | `~/.local/opt/chatgpt` |
| Ejecutable | `~/.local/opt/chatgpt/usr/lib/chatgpt/ChatGPT` |
| Lanzador de terminal | `~/.local/bin/chatgpt` |
| Menú GNOME | `~/.local/share/applications/chatgpt.desktop` |
| Icono | `~/.local/share/icons/hicolor/256x256/apps/chatgpt.png` |
| Versión gestionada | `~/.local/opt/chatgpt/.managed-version` |

## Requisitos

- Linux x86_64.
- Entorno gráfico con Tkinter (incluido en el AppImage).
- `dpkg-deb` instalado en el sistema (habitual en Ubuntu/Debian).
- Conexión a Internet.
- Espacio libre suficiente: el paquete oficial supera los 500 MB.
- El AppImage puede requerir soporte FUSE en la distribución.

## Desarrollo

```bash
python3 src/chatgpt_manager.py
```

Para compilar y publicar, GitHub Actions construye el gestor en Ubuntu 20.04 y genera un AppImage x86_64. Los pushes a `main` o las etiquetas `v*` generan una publicación GitHub Release.

## Seguridad y límites

- No ejecuta `sudo`, `apt install`, `dpkg -i` ni modifica `/usr`, `/opt` del sistema o repositorios APT.
- Descarga el `.deb` por HTTPS desde `persistent.oaistatic.com`, dominio oficial utilizado por OpenAI.
- La versión se obtiene de los metadatos del paquete `.deb`.
- No se verifica una firma criptográfica independiente ni un hash publicado del archivo descargado.
- El gestor solo instala el paquete x64; ARM64 no está incluido en esta primera versión.
- No elimina `~/.config` ni datos personales al desinstalar.
- La extracción local no resuelve dependencias ausentes del sistema.
- ChatGPT Desktop para Linux está en preview; las funciones disponibles pueden variar.

## Autoría

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
**Licencia:** MIT
