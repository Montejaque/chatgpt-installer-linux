# Guía de instalación y uso — Codex Installer & Updater

## 1. Descargar y ejecutar el gestor

Descarga **Codex-Installer-Updater-x86_64.AppImage** desde la sección Releases del repositorio. En la carpeta de descarga ejecuta:

    chmod +x Codex-Installer-Updater-x86_64.AppImage
    ./Codex-Installer-Updater-x86_64.AppImage

No uses sudo. La AppImage es el gestor gráfico; el ejecutable de Codex se descarga al instalar.

## 2. Instalar o actualizar Codex

Pulsa **Instalar / actualizar**. El gestor consulta la última publicación del repositorio oficial de OpenAI, descarga el archivo Linux x86_64, verifica que contiene el ejecutable esperado y comprueba que puede ejecutarse. La instalación se realiza en tu carpeta personal, sin modificar directorios del sistema.

## 3. Comprobar la versión

Pulsa **Comprobar versión** para consultar la publicación oficial y comparar la versión disponible con la instalada. Si hay una nueva versión, utiliza Instalar / actualizar.

## 4. Accesos directos

El gestor crea el comando ~/.local/bin/codex y el acceso ~/.local/share/applications/codex.desktop. El acceso del menú GNOME inicia Codex CLI en un terminal.

## 5. Reparar accesos

Si el comando o el acceso del menú desaparecen, pulsa **Reparar accesos**. Esta opción vuelve a crear ambos accesos a partir de la instalación gestionada.

## 6. Desinstalar

Pulsa **Desinstalar** y confirma. Se elimina la copia gestionada de Codex y sus accesos directos. No se elimina ~/.codex, donde Codex conserva configuración, credenciales y sesiones, ni se borran tus proyectos.

## 7. Ubicaciones

- Aplicación: ~/.local/opt/codex
- Comando: ~/.local/bin/codex
- Menú GNOME: ~/.local/share/applications/codex.desktop
- Datos personales: ~/.codex (se conserva)

## 8. Requisitos y compatibilidad

Linux x86_64, entorno gráfico, conexión a Internet y soporte AppImage/FUSE. El gestor no necesita sudo, APT ni permisos de administrador. Esta versión gestiona el binario Linux x86_64 de Codex CLI.

## 9. Desarrollador y contacto

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
**Dirección:** Avenida Andalucía, 48 · 29360 Montejaque (Málaga)  
**Teléfono:** 633 402 959  
**Correo:** montejaque@puntosvuela.es  
**Web:** https://puntosvuela.es/centros/montejaque

Identidad visual: negro #171717 y amarillo #F3D54E.
