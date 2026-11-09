# Guía de instalación y uso

## 1. Ejecutar el gestor

Descarga `ChatGPT-Installer-x86_64.AppImage`, ejecuta `chmod +x` y abre el archivo. No uses `sudo`.

## 2. Instalar o actualizar

Pulsa **Instalar / actualizar**. El gestor descarga el `.deb` oficial de OpenAI, comprueba sus metadatos, extrae el contenido en una carpeta temporal y lo instala dentro de tu perfil de usuario. El paquete puede superar los 500 MB.

## 3. Acceso desde GNOME

El gestor crea `chatgpt.desktop` con `Categories=Development;IDE;` y copia el icono PNG oficial del paquete. GNOME lo clasifica como herramienta de Programación. Si no aparece de inmediato, cierra sesión y vuelve a entrar.

## 4. Comprobar y reparar

- **Comprobar instalación:** muestra versión y ruta registradas.
- **Reparar accesos:** vuelve a crear el lanzador de terminal, el icono y la entrada del menú.

## 5. Desinstalar

La desinstalación elimina únicamente la copia gestionada, el lanzador, el icono y el `.desktop`. No elimina preferencias, sesiones ni datos personales.

## 6. Compatibilidad

La aplicación oficial Linux está soportada en Ubuntu 24.04/26.04, Debian 13, Fedora 43/44 y Arch actual. Ubuntu 20.04 no está certificado por OpenAI. Extraer el `.deb` sin root no implica que sus bibliotecas sean compatibles con Ubuntu 20.04.
