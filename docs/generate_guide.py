from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.colors import HexColor
from pathlib import Path
import sys

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "Guia-Codex-Installer-Puntos-Vuela-Montejaque.pdf")
W, H = A4
INK, YELLOW = HexColor("#171717"), HexColor("#F3D54E")
PANEL, MUTED, LINE = HexColor("#F5F5F2"), HexColor("#686868"), HexColor("#E4E4E0")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Kicker", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name="Big", fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="Sub", fontName="Helvetica", fontSize=9, leading=13, textColor=HexColor("#383838")))
styles.add(ParagraphStyle(name="H2x", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK, spaceBefore=7, spaceAfter=6))
styles.add(ParagraphStyle(name="Bodyx", fontName="Helvetica", fontSize=8, leading=11, textColor=HexColor("#303030")))
styles.add(ParagraphStyle(name="Smallx", fontName="Helvetica", fontSize=7.2, leading=10, textColor=HexColor("#303030")))
styles.add(ParagraphStyle(name="Whitex", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.white))
styles.add(ParagraphStyle(name="Labelx", fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=MUTED))
def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(YELLOW)
    canvas.rect(0, H-5*mm, W, 5*mm, fill=1, stroke=0)
    canvas.setStrokeColor(LINE)
    canvas.line(19*mm, 13*mm, W-19*mm, 13*mm)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(19*mm, 8*mm, "PUNTO VUELA MONTEJAQUE  ·  CODEX INSTALLER & UPDATER")
    canvas.drawRightString(W-19*mm, 8*mm, str(doc.page).zfill(2))
    canvas.restoreState()
doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=19*mm, leftMargin=19*mm, topMargin=18*mm, bottomMargin=19*mm,
    title="Codex Installer & Updater — Guía de instalación", author="Francisco Javier Gallego Orellana")
cw = W-38*mm
story = [Spacer(1,3*mm), P("GUÍA RÁPIDA  /  LINUX x86_64","Kicker"), P("Codex Installer<br/>&amp; Updater","Big"),
    P("Instala y actualiza <b>Codex CLI de OpenAI</b> desde una interfaz gráfica, sin permisos de administrador y conservando tus datos personales.","Sub"), Spacer(1,5*mm)]
hero = Table([[P("GESTOR GRÁFICO PARA LINUX","Labelx")],[P("Una herramienta sencilla para mantener Codex CLI actualizado.","Whitex")],
    [P("La AppImage contiene el gestor. Codex se descarga desde las publicaciones oficiales de OpenAI cuando se solicita la instalación.","Smallx")]],colWidths=[cw])
hero.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),INK),("LEFTPADDING",(0,0),(-1,-1),13),("RIGHTPADDING",(0,0),(-1,-1),13),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story += [hero,Spacer(1,4*mm)]
features=Table([[P("<b>INSTALAR</b><br/>Descarga y configura","Smallx"),P("<b>ACTUALIZAR</b><br/>Consulta versiones","Smallx"),P("<b>REPARAR</b><br/>Restaura accesos","Smallx")]],colWidths=[cw/3]*3)
features.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#FFF8D8")),("BOX",(0,0),(-1,-1),0.6,HexColor("#E8D98C")),("INNERGRID",(0,0),(-1,-1),0.6,HexColor("#E8D98C")),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story += [features,P("Puesta en marcha","H2x")]
steps=[("01","Descarga la AppImage","Obtén <b>Codex-Installer-Updater-x86_64.AppImage</b> desde Releases."),("02","Permite su ejecución","Abre una terminal en la carpeta de descarga y ejecuta los comandos indicados."),("03","Abre el gestor","Inicia la AppImage y pulsa Instalar / actualizar para descargar Codex CLI.")]
st=Table([[P(n,"Whitex"),P("<b>"+title+"</b><br/>"+desc,"Smallx")] for n,title,desc in steps],colWidths=[16*mm,cw-16*mm])
st.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),YELLOW),("BACKGROUND",(1,0),(1,-1),colors.white),("BOX",(0,0),(-1,-1),0.5,LINE),("INNERGRID",(0,0),(-1,-1),0.5,LINE),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story += [st,Spacer(1,3*mm)]
cmd=Table([[P("<font name='Courier'>chmod +x Codex-Installer-Updater-x86_64.AppImage<br/>./Codex-Installer-Updater-x86_64.AppImage</font>","Smallx")]],colWidths=[cw])
cmd.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PANEL),("BOX",(0,0),(-1,-1),0.5,LINE),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story += [cmd,Spacer(1,2*mm),P("<b>Requisitos:</b> Linux x86_64, entorno gráfico, conexión a Internet y soporte AppImage/FUSE. No necesita sudo ni instalación de paquetes del sistema.","Smallx"),PageBreak()]
story += [Spacer(1,2*mm),P("USO Y CONFIGURACIÓN","Kicker"),P("Todo bajo control.","Big"),P("Las operaciones habituales para mantener Codex CLI actualizado y accesible.","Sub"),P("Funciones del gestor","H2x")]
grid=Table([[P("<b>Instalar / actualizar</b><br/>Descarga el binario Linux x86_64 de la publicación oficial de OpenAI y lo instala en tu perfil.","Smallx"),P("<b>Comprobar versión</b><br/>Compara la versión instalada con la última publicación oficial.","Smallx")],
[P("<b>Reparar accesos</b><br/>Vuelve a crear el comando de terminal y el acceso del menú GNOME.","Smallx"),P("<b>Desinstalar</b><br/>Elimina la copia gestionada y sus accesos, sin borrar datos personales.","Smallx")]],colWidths=[cw/2]*2)
grid.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.6,LINE),("INNERGRID",(0,0),(-1,-1),0.6,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story += [grid,P("Dónde se instala","H2x")]
paths=[["Aplicación","~/.local/opt/codex"],["Comando","~/.local/bin/codex"],["Menú GNOME","~/.local/share/applications/codex.desktop"],["Configuración y sesiones","~/.codex (se conserva)"]]
pt=Table([[P("<b>"+a+"</b>","Smallx"),P("<font name='Courier'>"+b+"</font>","Smallx")] for a,b in paths],colWidths=[48*mm,cw-48*mm])
pt.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),PANEL),("BOX",(0,0),(-1,-1),0.6,LINE),("INNERGRID",(0,0),(-1,-1),0.5,LINE),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
story += [pt,P("Tus datos siguen siendo tuyos","H2x")]
safe=Table([[P("<b>Actualizar:</b> sustituye la copia gestionada. <b>Desinstalar:</b> elimina la aplicación y sus accesos. En ambos casos se conserva ~/.codex, con tus credenciales, ajustes y sesiones, y no se modifican tus proyectos.","Smallx")]],colWidths=[cw])
safe.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#FFF8D8")),("BOX",(0,0),(-1,-1),0.6,HexColor("#E8D98C")),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story += [safe,P("Desarrollador y contacto","H2x")]
contact=Table([[P("<b>DESARROLLADOR</b><br/>Francisco Javier Gallego Orellana<br/><br/><b>PUNTO VUELA MONTEJAQUE</b><br/>Avenida Andalucía, 48<br/>29360 Montejaque (Málaga)","Smallx"),
P("<b>CONTACTO</b><br/>Teléfono: 633 402 959<br/>Correo: montejaque@puntosvuela.es<br/>Web: puntosvuela.es/centros/montejaque","Smallx")]],colWidths=[cw/2]*2)
contact.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.6,LINE),("LINEBEFORE",(1,0),(1,0),0.6,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story += [contact,Spacer(1,3*mm),P("<b>Origen:</b> Codex CLI es un producto de OpenAI. Este gestor descarga el binario publicado en github.com/openai/codex. Identidad visual: negro #171717 y amarillo #F3D54E.","Smallx")]
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print("PDF generado:",OUT)
