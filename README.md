# Codex Installer & Updater — Punto Vuela Montejaque

Gestor gráfico para **OpenAI Codex CLI** en Linux x86_64. Permite consultar la versión oficial, instalar, actualizar, comprobar la instalación, reparar accesos y desinstalar la copia administrada.

> Este proyecto instala **Codex CLI**, el agente de programación que funciona en terminal. No instala ChatGPT Desktop ni la aplicación de escritorio Codex.

## Descarga

- [Último Release y AppImage](https://github.com/Montejaque/chatgpt-installer-linux/releases/latest)
- [Todos los Releases](https://github.com/Montejaque/chatgpt-installer-linux/releases)
- [Compilaciones de GitHub Actions](https://github.com/Montejaque/chatgpt-installer-linux/actions)

Descarga **Codex-Installer-Updater-x86_64.AppImage**, dale permiso de ejecución y ábrelo:

    chmod +x Codex-Installer-Updater-x86_64.AppImage
    ./Codex-Installer-Updater-x86_64.AppImage

No necesita sudo. La AppImage contiene el gestor gráfico; el ejecutable Codex se descarga desde las publicaciones oficiales de OpenAI cuando se pulsa **Instalar / actualizar**.

## Funciones

- Consulta la última publicación de openai/codex.
- Descarga el binario oficial codex-x86_64-unknown-linux-musl.tar.gz.
- Comprueba el nombre, origen y ejecución del binario descargado.
- Instala y actualiza de forma atómica en el perfil del usuario.
- Comprueba la versión instalada y la disponible.
- Repara el lanzador de terminal y el acceso del menú GNOME.
- Desinstala solo la copia administrada por esta herramienta.
- Conserva ~/.codex, credenciales, sesiones, ajustes y proyectos.

## Rutas de instalación

| Elemento | Ubicación |
|---|---|
| Aplicación | ~/.local/opt/codex |
| Ejecutable | ~/.local/opt/codex/codex |
| Comando | ~/.local/bin/codex |
| Menú GNOME | ~/.local/share/applications/codex.desktop |
| Configuración y sesiones | ~/.codex (se conserva) |

## Requisitos

- Linux x86_64.
- Entorno gráfico con Tkinter (incluido en la AppImage del gestor).
- Conexión a Internet para consultar y descargar Codex.
- Soporte FUSE o ejecución compatible de AppImage en la distribución.

La AppImage se compila en GitHub Actions. El gestor no ejecuta sudo, no instala paquetes del sistema y no modifica /usr, /opt ni la configuración global del sistema.

## Desarrollo

    python3 -m unittest discover -s tests -v
    python3 src/codex_manager.py

GitHub Actions compila la AppImage, genera la guía PDF, calcula SHA256 y publica los archivos en un GitHub Release cuando se actualiza main.

## Fuente oficial

- Codex CLI: https://github.com/openai/codex
- Instalación oficial: https://chatgpt.com/codex/install.sh
- Documentación: https://developers.openai.com/codex

## Autoría

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
Avenida Andalucía, 48 · 29360 Montejaque (Málaga)  
Teléfono: 633 402 959  
Correo: montejaque@puntosvuela.es  
Web: https://puntosvuela.es/centros/montejaque

**Licencia:** MIT
