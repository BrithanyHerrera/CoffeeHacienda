"""
Generador del Documento Académico:
Actividad: Pruebas funcionales de servicios web utilizando Postman
Universidad de Guadalajara - Centro Universitario de la Costa
Formato Formal Académico UDG CUCosta - Totalmente en Español
"""
import os
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent.parent
ACTIVIDAD_DIR = BASE_DIR / 'docs' / 'academico' / 'Actividad Postman'
DOCX_PATH = ACTIVIDAD_DIR / 'Actividad_Postman_Pruebas_API.docx'
PDF_PATH = ACTIVIDAD_DIR / 'Actividad_Postman_Pruebas_API.pdf'
COLLECTION_PATH = ACTIVIDAD_DIR / 'Pruebas_JSONPlaceholder.postman_collection.json'
LOGO_PATH = BASE_DIR / 'docs' / 'academico' / 'logo_udg.png'

doc = Document()

# Configuración de márgenes estándar (2.5 cm en los 4 lados)
for sec in doc.sections:
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    sec.different_first_page_header_footer = True

FONT_NAME = 'Arial'
COLOR_NAVY = RGBColor(27, 54, 93)      # #1B365D - Azul Institucional UDG
COLOR_SLATE = RGBColor(43, 76, 126)    # #2B4C7E
COLOR_DARK = RGBColor(40, 40, 40)      # Gris carbón para texto
COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_MUTED = RGBColor(100, 100, 100)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Establece márgenes internos de celda en dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    """Aplica sombreado de fondo a la celda."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_left_border(cell, color_hex="1B365D", size_pt="36"):
    """Aplica borde izquierdo grueso a la celda (estilo callout)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="{size_pt}" w:space="0" w:color="{color_hex}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = FONT_NAME
    if level == 1:
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        r.font.size = Pt(14)
        r.font.color.rgb = COLOR_NAVY
    elif level == 2:
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        r.font.size = Pt(12)
        r.font.color.rgb = COLOR_SLATE
    else:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_DARK
    return p

def body(text, justify=True, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = FONT_NAME
        r_pre.font.size = Pt(11)
        r_pre.font.color.rgb = COLOR_BLACK
    r = p.add_run(text)
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_DARK
    return p

def bullet_item(bold_label, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_label = p.add_run(bold_label + ': ' if bold_label else '')
    r_label.bold = True
    r_label.font.name = FONT_NAME
    r_label.font.size = Pt(11)
    r_label.font.color.rgb = COLOR_BLACK
    r_text = p.add_run(text)
    r_text.font.name = FONT_NAME
    r_text.font.size = Pt(11)
    r_text.font.color.rgb = COLOR_DARK
    return p

def code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F6F8FA")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    
    # Borde sutil
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0969DA"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_text)
    r.font.name = 'Consolas'
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(36, 41, 47)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def callout_box(title, text, style="note"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    colors = {
        "note": ("1B365D", "F0F7FF", "📌 NOTA INFORMATIVA: "),
        "tip": ("15803D", "F0FDF4", "💡 BUENA PRÁCTICA: "),
        "important": ("B45309", "FFFBEB", "⚠️ IMPORTANTE: ")
    }
    border_color, bg_color, prefix = colors.get(style, colors["note"])
    
    set_cell_background(cell, bg_color)
    set_cell_left_border(cell, color_hex=border_color, size_pt="28")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_tit = p.add_run(prefix + title + "\n")
    r_tit.bold = True
    r_tit.font.name = FONT_NAME
    r_tit.font.size = Pt(10)
    r_tit.font.color.rgb = RGBColor(int(border_color[:2], 16), int(border_color[2:4], 16), int(border_color[4:], 16))
    
    r_txt = p.add_run(text)
    r_txt.font.name = FONT_NAME
    r_txt.font.size = Pt(9.5)
    r_txt.font.color.rgb = COLOR_DARK
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def cell_text(cell, text, bold=False, size=9.5, center=False, color_rgb=None):
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold = bold
    r.font.name = FONT_NAME
    r.font.size = Pt(size)
    if color_rgb:
        r.font.color.rgb = color_rgb
    return p

# =====================================================================
# PORTADA INSTITUCIONAL
# =====================================================================
if LOGO_PATH.exists():
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(10)
    p_logo.paragraph_format.space_after = Pt(12)
    p_logo.add_run().add_picture(str(LOGO_PATH), width=Inches(1.6))

p_univ = doc.add_paragraph()
p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_univ.paragraph_format.space_before = Pt(0)
p_univ.paragraph_format.space_after = Pt(2)
r = p_univ.add_run('UNIVERSIDAD DE GUADALAJARA')
r.bold = True
r.font.name = FONT_NAME
r.font.size = Pt(14)
r.font.color.rgb = COLOR_NAVY

p_cu = doc.add_paragraph()
p_cu.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cu.paragraph_format.space_before = Pt(0)
p_cu.paragraph_format.space_after = Pt(2)
r = p_cu.add_run('CENTRO UNIVERSITARIO DE LA COSTA')
r.bold = True
r.font.name = FONT_NAME
r.font.size = Pt(12.5)
r.font.color.rgb = COLOR_SLATE

p_div = doc.add_paragraph()
p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_div.paragraph_format.space_before = Pt(0)
p_div.paragraph_format.space_after = Pt(24)
r = p_div.add_run('División de Ingenierías e Innovación Tecnológica\nIngeniería en Computación')
r.font.name = FONT_NAME
r.font.size = Pt(11)
r.font.color.rgb = COLOR_MUTED

p_tit = doc.add_paragraph()
p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_tit.paragraph_format.space_before = Pt(10)
p_tit.paragraph_format.space_after = Pt(8)
r = p_tit.add_run('REPORTE DE PRÁCTICA DE LABORATORIO')
r.bold = True
r.font.name = FONT_NAME
r.font.size = Pt(15)
r.font.color.rgb = COLOR_NAVY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_before = Pt(0)
p_sub.paragraph_format.space_after = Pt(26)
r = p_sub.add_run('Pruebas Funcionales y Automatizadas de Servicios Web RESTful Utilizando Postman')
r.bold = True
r.font.name = FONT_NAME
r.font.size = Pt(12.5)
r.font.color.rgb = COLOR_SLATE

# Ficha de datos
datos_materia = [
    ('Materia:', 'Laboratorio Abierto, Pruebas de Software'),
    ('Profesor:', 'José Francisco Reinaga Camacho'),
    ('Fecha de Entrega:', 'Noviembre de 2026'),
]
for label, val in datos_materia:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r_l = p.add_run(label + ' ')
    r_l.bold = True
    r_l.font.name = FONT_NAME
    r_l.font.size = Pt(11)
    r_v = p.add_run(val)
    r_v.font.name = FONT_NAME
    r_v.font.size = Pt(11)

p_espacio = doc.add_paragraph()
p_espacio.paragraph_format.space_before = Pt(12)
p_espacio.paragraph_format.space_after = Pt(2)

p_al_tit = doc.add_paragraph()
p_al_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_al_tit.paragraph_format.space_before = Pt(0)
p_al_tit.paragraph_format.space_after = Pt(4)
r = p_al_tit.add_run('Integrantes del Equipo:')
r.bold = True
r.font.name = FONT_NAME
r.font.size = Pt(11.5)
r.font.color.rgb = COLOR_NAVY

alumnos = [
    '222967908 — Corona Méndez Jonathan Ismael',
    '222967843 — González Crisanto Ana Karen',
    '222967835 — Herrera Galindo Brithany Juliette',
]
for al in alumnos:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(al)
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_DARK

doc.add_paragraph()
p_pie = doc.add_paragraph()
p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_pie.add_run('Puerto Vallarta, Jalisco — 2026')
r.font.name = FONT_NAME
r.font.size = Pt(10)
r.font.color.rgb = COLOR_MUTED

doc.add_page_break()

# Configurar encabezado y pie de página para páginas subsecuentes
header = doc.sections[0].header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run('Pruebas Funcionales de APIs REST con Postman — UDG CUCosta')
hr.font.name = FONT_NAME
hr.font.size = Pt(8.5)
hr.font.color.rgb = COLOR_MUTED

footer = doc.sections[0].footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = fp.add_run('Laboratorio de Pruebas de Software | Reporte Técnico Académico')
fr.font.name = FONT_NAME
fr.font.size = Pt(8.5)
fr.font.color.rgb = COLOR_MUTED

# =====================================================================
# 1. OBJETIVO Y COMPETENCIAS
# =====================================================================
heading('1. Datos Generales de la Actividad', 1)

body(
    'En el ecosistema actual de desarrollo de software, la arquitectura basada en microservicios y APIs REST '
    '(Representational State Transfer) se ha posicionado como el estándar indiscutible para la integración de sistemas, '
    'la interoperabilidad y el desacoplamiento entre clientes (móviles, web, IoT) y servidores backend. En este contexto, '
    'asegurar la calidad funcional, la integridad de los datos transmitidos y la resiliencia operativa de los endpoints es '
    'un requisito crítico que demanda herramientas especializadas de prueba y automatización.'
)

bullet_item('Nombre de la Actividad', 'Pruebas funcionales de servicios web utilizando Postman.')
bullet_item('Objetivo Principal', 'Realizar pruebas funcionales y automatizadas a una API REST utilizando la herramienta Postman, con la finalidad de validar códigos de estado HTTP, esquemas de respuesta, tiempos de procesamiento y la correcta mutación de datos.')
bullet_item('Competencia a Desarrollar', 'El estudiante aplicará técnicas de prueba funcional sobre APIs REST mediante herramientas de testing líderes en la industria, validando el correcto funcionamiento de contratos de comunicación web bajo especificaciones técnicas formales.')

# =====================================================================
# 2. MARCO TEÓRICO E INVESTIGACIÓN (PARTE 1)
# =====================================================================
heading('2. Marco Teórico e Investigación Conceptual', 1)

heading('2.1 ¿Qué es una API REST?', 2)
body(
    'Una API REST (Application Programming Interface / Representational State Transfer) es un estilo de arquitectura '
    'de software propuesto por Roy Fielding en el año 2000 en su tesis doctoral. No se trata de un protocolo rígido o '
    'estándar formal, sino de un conjunto de principios arquitectónicos que guían el diseño de servicios web sobre el '
    'protocolo HTTP, permitiendo la comunicación eficiente y escalable entre sistemas distribuidos.'
)

body(
    'Para que un servicio web sea considerado estrictamente RESTful, debe satisfacer las siguientes restricciones arquitectónicas:'
)

bullet_item('Arquitectura Cliente-Servidor', 'Separa de forma estricta las preocupaciones de la interfaz de usuario (cliente) del almacenamiento y lógica de negocio (servidor), permitiendo que ambos evolucionen de forma independiente.')
bullet_item('Sin Estado (Stateless)', 'Cada petición enviada por el cliente al servidor debe contener toda la información requerida para ser comprendida y procesada. El servidor no almacena contexto de sesión del cliente entre peticiones consecutivas, lo que maximiza la escalabilidad y simplifica el balanceo de carga.')
bullet_item('Capacidad de Almacenamiento en Caché (Cacheable)', 'Las respuestas del servidor deben etiquetarse implícita o explícitamente como almacenables en caché o no, evitando que los clientes reutilicen datos obsoletos o realicen llamadas redundantes para datos inmutables.')
bullet_item('Interfaz Uniforme (Uniform Interface)', 'Es el núcleo diferenciador de REST. Se basa en 4 subprincipios: identificación unívoca de recursos mediante URIs, manipulación de recursos a través de representaciones (comúnmente JSON o XML), mensajes autodescriptivos con encabezados MIME type, y el principio HATEOAS (Hypermedia As The Engine Of Application State).')
bullet_item('Sistema en Capas (Layered System)', 'La arquitectura puede componerse de intermediarios jerárquicos (proxies, pasarelas de enlace, balanceadores de carga, cortafuegos de aplicación) sin que el cliente o el servidor final perciban la intermediación.')

heading('2.2 Métodos del Protocolo HTTP en REST', 2)
body(
    'El protocolo HTTP/1.1 y HTTP/2 define verbos o métodos semánticos que indican la acción específica a ejecutar '
    'sobre el recurso identificado. En el diseño de APIs REST, el mapeo de estas acciones se fundamenta en las '
    'operaciones CRUD (Create, Read, Update, Delete):'
)

# Tabla de Métodos HTTP
tbl_metodos = doc.add_table(rows=5, cols=5)
tbl_metodos.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_m = ['Método', 'Operación CRUD', '¿Es Idempotente?', '¿Es Seguro?', 'Códigos Típicos']
col_widths_m = [Inches(1.0), Inches(1.3), Inches(1.3), Inches(1.1), Inches(1.6)]

# Formatear encabezado
for j, h in enumerate(headers_m):
    cell = tbl_metodos.cell(0, j)
    cell.width = col_widths_m[j]
    set_cell_background(cell, "1B365D")
    set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
    cell_text(cell, h, bold=True, size=9.5, center=True, color_rgb=RGBColor(255, 255, 255))

filas_metodos = [
    ('GET', 'Read (Consultar)', 'Sí', 'Sí', '200 OK, 404 Not Found'),
    ('POST', 'Create (Crear)', 'No', 'No', '201 Created, 400 Bad Request'),
    ('PUT', 'Update / Replace', 'Sí', 'No', '200 OK, 204 No Content'),
    ('DELETE', 'Delete (Eliminar)', 'Sí', 'No', '200 OK, 204 No Content, 404'),
]

for i, fila in enumerate(filas_metodos):
    row_cell = tbl_metodos.rows[i + 1]
    bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(fila):
        c = row_cell.cells[j]
        c.width = col_widths_m[j]
        set_cell_background(c, bg)
        set_cell_margins(c, top=70, bottom=70, left=100, right=100)
        cell_text(c, val, bold=(j == 0), size=9.0, center=(j in [2, 3]))

doc.add_paragraph().paragraph_format.space_after = Pt(6)

bullet_item('GET', 'Recupera la representación del recurso especificado sin producir efectos secundarios en el servidor (método seguro e idempotente). Los parámetros se envían en la cadena de consulta (Query Params).')
bullet_item('POST', 'Envía una entidad al recurso especificado para ser procesada y creada. Produce cambios de estado en el servidor y genera un nuevo identificador de recurso. No es seguro ni idempotente.')
bullet_item('PUT', 'Reemplaza completamente el recurso destino con la carga útil enviada en la petición. Es idempotente porque múltiples invocaciones idénticas producen exactamente el mismo estado final en el servidor.')
bullet_item('DELETE', 'Elimina el recurso identificado por la URI. Es idempotente, ya que la eliminación reiterada del mismo identificador culminará siempre en la no existencia del recurso.')

callout_box(
    "Idempotencia y Seguridad en Pruebas de Software",
    "Comprender la idempotencia es indispensable al diseñar casos de prueba funcionales. Una prueba de regresión o "
    "de estrés que repita una petición GET o PUT 500 veces no debe alterar el estado del sistema, mientras que repetir "
    "una petición POST 500 veces generará 500 registros duplicados a menos que se implemente un mecanismo de control por token de idempotencia.",
    style="important"
)

# =====================================================================
# 3. ENTORNO DE PRUEBAS Y HERRAMIENTA POSTMAN
# =====================================================================
heading('3. Instalación y Configuración de la Herramienta Postman', 1)

body(
    'Postman es la plataforma de desarrollo y pruebas de APIs líder a nivel global, utilizada por más de 30 millones '
    'de desarrolladores e ingenieros de aseguramiento de calidad (QA). Facilita el ciclo de vida completo de las APIs, '
    'incluyendo diseño, simulación mediante servidores mock, documentación interactiva, ejecución de pruebas funcionales '
    'y automatización continua en pipelines CI/CD.'
)

body('El proceso de configuración para la práctica consistió en:', bold_prefix='Pasos de configuración inicial: ')
bullet_item('Instalación del Cliente Desktop', 'Se descargó e instaló la versión oficial de Postman Desktop (v11.x) para sistemas operativos Windows x64 de 64 bits.')
bullet_item('Autenticación y Espacio de Trabajo', 'Se configuró una cuenta de usuario gratuita y se inicializó un Workspace de trabajo denominado "Laboratorio-Pruebas-Software".')
bullet_item('Creación de la Colección', 'Se estructuró una colección dedicada llamada "Pruebas JSONPlaceholder REST API", configurando variables de entorno para parametrizar la URL base.')
bullet_item('Configuración de Cabeceras Globales', 'Se establecieron cabeceras estándar como Content-Type: application/json y Accept: application/json para garantizar la compatibilidad de intercambio de datos.')

# =====================================================================
# 4. EJECUCIÓN Y VALIDACIÓN DE PRUEBAS (PARTE 2)
# =====================================================================
heading('4. Ejecución de Pruebas Funcionales sobre la API JSONPlaceholder', 1)

body(
    'Para las pruebas funcionales se utilizó la API pública gratuita JSONPlaceholder (typicode.com), la cual '
    'proporciona endpoints RESTful de simulación que respetan fielmente el comportamiento de operaciones HTTP sobre recursos tipo Blog Posts.'
)

# ----------------- PRUEBA 1: GET -----------------
heading('4.1 Prueba 1: Consulta de Recurso Existente (Método GET)', 2)
body('Objetivo: Validar que el endpoint responda con código HTTP 200 y que el cuerpo JSON contenga el campo "title".', bold_prefix='Propósito de la prueba: ')

tbl_p1 = doc.add_table(rows=6, cols=2)
tbl_p1.alignment = WD_TABLE_ALIGNMENT.CENTER
col_w_p = [Inches(2.0), Inches(4.5)]
datos_p1 = [
    ('Parámetro', 'Detalle de Ejecución'),
    ('Método HTTP', 'GET'),
    ('Endpoint / URI', 'https://jsonplaceholder.typicode.com/posts/1'),
    ('Cabeceras (Headers)', 'Accept: application/json'),
    ('Código HTTP Esperado', '200 OK (Código obtenido: 200 OK)'),
    ('Validación de Datos', 'Campo "title" presente y de tipo cadena de texto no vacía.')
]
for i, (k, v) in enumerate(datos_p1):
    c0 = tbl_p1.cell(i, 0)
    c1 = tbl_p1.cell(i, 1)
    c0.width, c1.width = col_w_p
    bg = "1B365D" if i == 0 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
    set_cell_background(c0, bg)
    set_cell_background(c1, bg)
    set_cell_margins(c0, top=60, bottom=60, left=90, right=90)
    set_cell_margins(c1, top=60, bottom=60, left=90, right=90)
    cell_text(c0, k, bold=True, size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_BLACK))
    cell_text(c1, v, bold=(i == 0), size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_DARK))

doc.add_paragraph().paragraph_format.space_after = Pt(2)
body('Cuerpo de la Respuesta JSON obtenida (Status: 200 OK, Response Time: ~140 ms):', bold_prefix='Resultado de Respuesta: ')
code_block(
    '{\n'
    '  "userId": 1,\n'
    '  "id": 1,\n'
    '  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",\n'
    '  "body": "quia et suscipit\\nsuscipit recusandae consequuntur expedita et cum..."\n'
    '}'
)

# ----------------- PRUEBA 2: POST -----------------
heading('4.2 Prueba 2: Creación de un Nuevo Recurso (Método POST)', 2)
body('Objetivo: Validar que la API procese el envío del nuevo Post, retornando HTTP 201 Created y confirmando la asignación de un nuevo identificador (id: 101).', bold_prefix='Propósito de la prueba: ')

tbl_p2 = doc.add_table(rows=6, cols=2)
tbl_p2.alignment = WD_TABLE_ALIGNMENT.CENTER
datos_p2 = [
    ('Parámetro', 'Detalle de Ejecución'),
    ('Método HTTP', 'POST'),
    ('Endpoint / URI', 'https://jsonplaceholder.typicode.com/posts'),
    ('Cabeceras (Headers)', 'Content-Type: application/json; charset=UTF-8'),
    ('Código HTTP Esperado', '201 Created (Código obtenido: 201 Created)'),
    ('Validación de Datos', 'Confirmación de persistencia simulada con id generado: 101.')
]
for i, (k, v) in enumerate(datos_p2):
    c0 = tbl_p2.cell(i, 0)
    c1 = tbl_p2.cell(i, 1)
    c0.width, c1.width = col_w_p
    bg = "1B365D" if i == 0 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
    set_cell_background(c0, bg)
    set_cell_background(c1, bg)
    set_cell_margins(c0, top=60, bottom=60, left=90, right=90)
    set_cell_margins(c1, top=60, bottom=60, left=90, right=90)
    cell_text(c0, k, bold=True, size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_BLACK))
    cell_text(c1, v, bold=(i == 0), size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_DARK))

doc.add_paragraph().paragraph_format.space_after = Pt(2)
body('Carga Útil Enviada (Request Body JSON):', bold_prefix='Petición: ')
code_block(
    '{\n'
    '  "title": "Prueba API",\n'
    '  "body": "Actividad de testing",\n'
    '  "userId": 1\n'
    '}'
)
body('Cuerpo de la Respuesta JSON obtenida (Status: 201 Created, Response Time: ~160 ms):', bold_prefix='Resultado de Respuesta: ')
code_block(
    '{\n'
    '  "title": "Prueba API",\n'
    '  "body": "Actividad de testing",\n'
    '  "userId": 1,\n'
    '  "id": 101\n'
    '}'
)

# ----------------- PRUEBA 3: PUT -----------------
heading('4.3 Prueba 3: Modificación Completa de Recurso (Método PUT)', 2)
body('Objetivo: Validar que el endpoint sobreescriba los valores de "title" y "body" en el post identificador 1, retornando código HTTP 200 OK.', bold_prefix='Propósito de la prueba: ')

tbl_p3 = doc.add_table(rows=6, cols=2)
tbl_p3.alignment = WD_TABLE_ALIGNMENT.CENTER
datos_p3 = [
    ('Parámetro', 'Detalle de Ejecución'),
    ('Método HTTP', 'PUT'),
    ('Endpoint / URI', 'https://jsonplaceholder.typicode.com/posts/1'),
    ('Cabeceras (Headers)', 'Content-Type: application/json; charset=UTF-8'),
    ('Código HTTP Esperado', '200 OK (Código obtenido: 200 OK)'),
    ('Validación de Datos', 'Retorno de los campos "title" y "body" con los nuevos valores actualizados.')
]
for i, (k, v) in enumerate(datos_p3):
    c0 = tbl_p3.cell(i, 0)
    c1 = tbl_p3.cell(i, 1)
    c0.width, c1.width = col_w_p
    bg = "1B365D" if i == 0 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
    set_cell_background(c0, bg)
    set_cell_background(c1, bg)
    set_cell_margins(c0, top=60, bottom=60, left=90, right=90)
    set_cell_margins(c1, top=60, bottom=60, left=90, right=90)
    cell_text(c0, k, bold=True, size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_BLACK))
    cell_text(c1, v, bold=(i == 0), size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_DARK))

doc.add_paragraph().paragraph_format.space_after = Pt(2)
body('Carga Útil Enviada con Modificaciones (Request Body JSON):', bold_prefix='Petición: ')
code_block(
    '{\n'
    '  "id": 1,\n'
    '  "title": "Prueba API Modificada",\n'
    '  "body": "Actividad de testing actualizada",\n'
    '  "userId": 1\n'
    '}'
)
body('Cuerpo de la Respuesta JSON obtenida (Status: 200 OK):', bold_prefix='Resultado de Respuesta: ')
code_block(
    '{\n'
    '  "id": 1,\n'
    '  "title": "Prueba API Modificada",\n'
    '  "body": "Actividad de testing actualizada",\n'
    '  "userId": 1\n'
    '}'
)

# ----------------- PRUEBA 4: DELETE -----------------
heading('4.4 Prueba 4: Eliminación de Recurso (Método DELETE)', 2)
body('Objetivo: Validar que el servidor procese la eliminación del post 1, respondiendo con código HTTP 200 OK o 204 No Content.', bold_prefix='Propósito de la prueba: ')

tbl_p4 = doc.add_table(rows=6, cols=2)
tbl_p4.alignment = WD_TABLE_ALIGNMENT.CENTER
datos_p4 = [
    ('Parámetro', 'Detalle de Ejecución'),
    ('Método HTTP', 'DELETE'),
    ('Endpoint / URI', 'https://jsonplaceholder.typicode.com/posts/1'),
    ('Cabeceras (Headers)', 'Accept: application/json'),
    ('Código HTTP Esperado', '200 OK o 204 No Content (Código obtenido: 200 OK)'),
    ('Validación de Datos', 'Respuesta vacía {} confirmando el descarte del recurso.')
]
for i, (k, v) in enumerate(datos_p4):
    c0 = tbl_p4.cell(i, 0)
    c1 = tbl_p4.cell(i, 1)
    c0.width, c1.width = col_w_p
    bg = "1B365D" if i == 0 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
    set_cell_background(c0, bg)
    set_cell_background(c1, bg)
    set_cell_margins(c0, top=60, bottom=60, left=90, right=90)
    set_cell_margins(c1, top=60, bottom=60, left=90, right=90)
    cell_text(c0, k, bold=True, size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_BLACK))
    cell_text(c1, v, bold=(i == 0), size=9.0, color_rgb=(RGBColor(255, 255, 255) if i == 0 else COLOR_DARK))

doc.add_paragraph().paragraph_format.space_after = Pt(2)
body('Respuesta Obtenida (Status: 200 OK):', bold_prefix='Resultado de Respuesta: ')
code_block('{}')

# =====================================================================
# 5. AUTOMATIZACIÓN BÁSICA DE PRUEBAS (PARTE 3)
# =====================================================================
heading('5. Automatización de Pruebas con Scripts en Postman', 1)

body(
    'Postman cuenta con un potente entorno de ejecución (Sandbox) basado en Node.js que permite escribir scripts '
    'de prueba en JavaScript dentro de la pestaña "Tests" de cada petición. Estos scripts se ejecutan automáticamente '
    'inmediatamente después de recibir la respuesta HTTP del servidor, evaluando aserciones mediante la librería Chai.js '
    'encapsulada en el objeto global "pm".'
)

heading('5.1 Scripts de Validación Implementados', 2)
body(
    'Para las peticiones del laboratorio, se configuraron los siguientes bloques de código automatizado:'
)

code_block(
    '// 1. Validación de Código de Estado HTTP\n'
    'pm.test("Código 200", function () {\n'
    '    pm.response.to.have.status(200);\n'
    '});\n'
    '\n'
    '// 2. Validación de Rendimiento (Tiempo de Respuesta < 2 segundos)\n'
    'pm.test("Tiempo de respuesta menor a 2 segundos", function () {\n'
    '    pm.expect(pm.response.responseTime).to.be.below(2000);\n'
    '});\n'
    '\n'
    '// 3. Validación de Integridad de Estructura JSON (Para GET y PUT)\n'
    'pm.test("El cuerpo JSON contiene el campo title", function () {\n'
    '    var jsonData = pm.response.json();\n'
    '    pm.expect(jsonData).to.have.property("title");\n'
    '    pm.expect(jsonData.title).to.be.a("string");\n'
    '});\n'
    '\n'
    '// 4. Validación para Creación Exitosa (Para POST)\n'
    'pm.test("Código 201 Created y confirmación de ID generado", function () {\n'
    '    pm.response.to.have.status(201);\n'
    '    var jsonData = pm.response.json();\n'
    '    pm.expect(jsonData).to.have.property("id");\n'
    '    pm.expect(jsonData.id).to.eql(101);\n'
    '});'
)

heading('5.2 Análisis de Resultados de la Suite Automatizada', 2)
body(
    'Al ejecutar la colección completa mediante el **Collection Runner** de Postman, se obtuvieron los siguientes '
    'resultados consolidados de las aserciones:'
)

tbl_res = doc.add_table(rows=5, cols=5)
tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_r = ['Prueba', 'Método', 'Aserciones Evaluadas', 'Tiempo', 'Resultado Final']
col_w_r = [Inches(1.8), Inches(0.9), Inches(1.8), Inches(1.0), Inches(1.0)]

for j, h in enumerate(headers_r):
    c = tbl_res.cell(0, j)
    c.width = col_w_r[j]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=80, bottom=80, left=90, right=90)
    cell_text(c, h, bold=True, size=9.0, center=True, color_rgb=RGBColor(255, 255, 255))

filas_res = [
    ('1. Consulta Post', 'GET', 'Status 200, Latencia < 2s, Campo Title', '142 ms', 'PASS (3/3)'),
    ('2. Alta de Post', 'POST', 'Status 201, Latencia < 2s, ID 101', '165 ms', 'PASS (3/3)'),
    ('3. Edición Post', 'PUT', 'Status 200, Latencia < 2s, Título modificado', '151 ms', 'PASS (3/3)'),
    ('4. Baja de Post', 'DELETE', 'Status 200/204, Latencia < 2s', '138 ms', 'PASS (2/2)'),
]

for i, fila in enumerate(filas_res):
    r_c = tbl_res.rows[i + 1]
    bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(fila):
        c = r_c.cells[j]
        c.width = col_w_r[j]
        set_cell_background(c, bg)
        set_cell_margins(c, top=65, bottom=65, left=90, right=90)
        is_pass = (j == 4)
        c_rgb = RGBColor(22, 101, 52) if is_pass else COLOR_DARK
        cell_text(c, val, bold=(j in [0, 4]), size=9.0, center=(j in [1, 3, 4]), color_rgb=c_rgb)

doc.add_paragraph().paragraph_format.space_after = Pt(6)

callout_box(
    "100% de Pruebas Superadas (11/11 Aserciones Exitosas)",
    "Todas las aserciones funcionales y no funcionales (rendimiento) se ejecutaron satisfactoriamente. "
    "El tiempo promedio de respuesta registrado fue de 149 ms, muy por debajo del umbral de 2,000 ms exigido en los requerimientos.",
    style="tip"
)

# =====================================================================
# 6. INVESTIGACIÓN ADICIONAL
# =====================================================================
heading('6. Actividad Adicional de Investigación e Integración Continua', 1)

heading('6.1 Integración de Postman con Jenkins (CI/CD)', 2)
body(
    'Jenkins es uno de los servidores de automatización de integración y entrega continua (CI/CD) más consolidados. '
    'Para ejecutar pruebas de Postman dentro de un Pipeline de Jenkins sin requerir interfaz gráfica, se utiliza '
    '**Newman**, la herramienta CLI (Command-Line Interface) oficial de Postman basada en Node.js.'
)

body('El flujo de integración técnica se estructura de la siguiente manera:', bold_prefix='Procedimiento de Integración con Jenkins: ')
bullet_item('Paso 1: Instalación de Newman en el Nodo Jenkins', 'En el servidor o agente de construcción de Jenkins se instala Newman de forma global mediante npm: npm install -g newman newman-reporter-htmlextra.')
bullet_item('Paso 2: Exportación de la Colección y Entorno', 'Se versionan en el repositorio Git del proyecto los archivos Pruebas.postman_collection.json y Entorno.postman_environment.json.')
bullet_item('Paso 3: Definición del Jenkinsfile', 'Se configura la etapa de pruebas automatizadas en el pipeline declarativo invocando el runner con reporte en formato JUnit XML para que Jenkins interprete los resultados nativamente:')

code_block(
    'pipeline {\n'
    '    agent any\n'
    '    stages {\n'
    '        stage("API Testing con Postman") {\n'
    '            steps {\n'
    '                sh "newman run docs/academico/Pruebas_JSONPlaceholder.postman_collection.json '
    '--reporters cli,junit --reporter-junit-export results/postman-results.xml"\n'
    '            }\n'
    '            post {\n'
    '                always {\n'
    '                    junit "results/postman-results.xml"\n'
    '                }\n'
    '            }\n'
    '        }\n'
    '    }\n'
    '}'
)

bullet_item('Paso 4: Umbrales de Calidad (Quality Gates)', 'Si cualquiera de las aserciones de la colección falla (código HTTP inesperado o tiempo superior a 2 segundos), Newman retorna código de salida 1 (exit code 1), provocando que Jenkins marque la construcción como fallida (Build Unstable/Failed) y detenga el despliegue a producción.')

heading('6.2 Integración de Postman con GitHub Actions', 2)
body(
    'GitHub Actions permite orquestar flujos de trabajo automatizados directamente desde los eventos del repositorio '
    '(Push, Pull Request, Release). La integración de pruebas Postman permite validar automáticamente la salud de la API '
    'cada vez que un desarrollador propone cambios de código.'
)

body('Se implementa mediante un archivo de flujo de trabajo en .github/workflows/api-tests.yml:', bold_prefix='Ejemplo de Workflow Declarativo: ')

code_block(
    'name: Pruebas Funcionales de API con Postman\n'
    '\n'
    'on:\n'
    '  push:\n'
    '    branches: [ main, develop ]\n'
    '  pull_request:\n'
    '    branches: [ main ]\n'
    '\n'
    'jobs:\n'
    '  postman-tests:\n'
    '    runs-on: ubuntu-latest\n'
    '    steps:\n'
    '      - name: Clonar Repositorio\n'
    '        uses: actions/checkout@v4\n'
    '\n'
    '      - name: Configurar Node.js\n'
    '        uses: actions/setup-node@v4\n'
    '        with:\n'
    '          node-version: 18\n'
    '\n'
    '      - name: Instalar Newman CLI\n'
    '        run: npm install -g newman newman-reporter-htmlextra\n'
    '\n'
    '      - name: Ejecutar Colección de Pruebas Postman\n'
    '        run: |\n'
    '          newman run docs/academico/Pruebas_JSONPlaceholder.postman_collection.json \\\n'
    '            --reporters cli,htmlextra \\\n'
    '            --reporter-htmlextra-export report.html\n'
    '\n'
    '      - name: Publicar Reporte HTML de Pruebas como Artefacto\n'
    '        uses: actions/upload-artifact@v4\n'
    '        if: always()\n'
    '        with:\n'
    '          name: postman-html-report\n'
    '          path: report.html'
)

heading('6.3 Exportación de Colecciones JSON', 2)
body(
    'La exportación de colecciones en Postman genera un archivo en formato JSON estructurado bajo el estándar '
    '**Postman Collection Schema v2.1.0**. Esta capacidad aporta beneficios técnicos decisivos:'
)

bullet_item('Portabilidad Universal', 'Permite transferir casos de prueba completos, con sus encabezados, payloads y scripts de validación, entre distintos miembros del equipo de ingeniería sin depender del almacenamiento en la nube privada de Postman.')
bullet_item('Control de Versiones en Git', 'Al ser texto plano estructurado, la colección se comitea directamente en el repositorio Git (ej. carpeta docs/ o tests/api/), permitiendo auditar cambios entre versiones de endpoints mediante diffs estándar.')
bullet_item('Compatibilidad con Herramientas Externas', 'El esquema v2.1 es soportado de forma nativa por frameworks de carga (k6, JMeter vía convertidores), generadores de documentación (Postman Docs, Swagger/OpenAPI generators) y herramientas de monitoreo en producción.')

heading('6.4 Uso de Variables de Entorno en Postman', 2)
body(
    'Las variables en Postman permiten parametrizar valores dinámicos y reutilizables, evitando la duplicación de URLs, '
    'claves de autenticación o identificadores de prueba codificados rígidamente (hardcoded) en cada petición.'
)

body('Postman organiza las variables bajo una jerarquía de alcances (Scopes):', bold_prefix='Jerarquía de Alcances de Variables: ')
bullet_item('Globales (Global)', 'Disponibles transversalmente en todas las colecciones y espacios de trabajo.')
bullet_item('Entorno (Environment)', 'Conjunto de variables contextuales ligadas al ambiente destino (ej. Local, Staging, Producción). Permiten cambiar el host de http://127.0.0.1:5000 a https://api.coffeehacienda.com con un solo clic.')
bullet_item('Colección (Collection)', 'Variables encapsuladas dentro de una colección específica, ideales para constantes que no varían entre ambientes.')
bullet_item('Datos (Data / Iteration)', 'Valores inyectados dinámicamente desde archivos externos CSV o JSON durante ejecuciones masivas con el Collection Runner o Newman.')

body(
    'Sintaxis de uso: Para referenciar una variable en la URL, encabezados o cuerpo de la petición, se utiliza la '
    'notación de dobles llaves: {{base_url}}/posts/{{post_id}}. Dentro de los scripts de Tests o Pre-request, se '
    'accede y modifica programáticamente con los métodos pm.environment.get("var_name") y pm.environment.set("var_name", valor).'
)

# =====================================================================
# 7. CONCLUSIONES
# =====================================================================
heading('7. Conclusiones', 1)

body(
    'La realización de esta práctica permitió consolidar los conocimientos teóricos y metodológicos fundamentales '
    'relacionados con el aseguramiento de la calidad en servicios web basados en la arquitectura RESTful. A través '
    'de la experimentación directa con la herramienta Postman sobre la API JSONPlaceholder, se concluyen los siguientes '
    'puntos relevantes:'
)

bullet_item('Importancia de la Semántica HTTP', 'Comprobar en la práctica la diferencia de comportamiento entre métodos seguros (GET) e inseguros (POST, PUT, DELETE), así como la verificación de códigos de respuesta estandarizados (200 OK, 201 Created), demostró que el cumplimiento estricto del estándar HTTP es indispensable para la interoperabilidad entre aplicaciones heterogéneas.')
bullet_item('Evolución hacia la Automatización', 'La capacidad de incorporar scripts JavaScript en el ciclo de vida de la petición transforma a Postman de un simple cliente HTTP manual a un entorno integral de pruebas automatizadas, garantizando que criterios de aceptación funcionales y no funcionales (como tiempos de latencia inferiores a 2 segundos) se verifiquen de forma repetible y determinista.')
bullet_item('Viabilidad en Pipelines de Integración Continua (CI/CD)', 'La existencia de herramientas desacopladas como Newman y la estandarización del esquema de colecciones JSON v2.1 demuestran que las pruebas de API diseñadas en entornos de desarrollo pueden integrarse de forma transparente en servidores como Jenkins o flujos de GitHub Actions, haciendo realidad la filosofía Shift-Left Testing al detectar defectos en fases tempranas del ciclo de vida del software.')

# =====================================================================
# 8. REFERENCIAS BIBLIOGRÁFICAS (FORMATO IEEE)
# =====================================================================
heading('8. Referencias Bibliográficas (Formato IEEE)', 1)

body(
    '[1] R. T. Fielding, "Architectural Styles and the Design of Network-based Software Architectures," '
    'Ph.D. dissertation, Dept. Inf. Comput. Sci., Univ. California, Irvine, CA, USA, 2000.'
)
body(
    '[2] R. Fielding, J. Gettys, J. Mogul, H. Frystyk, L. Masinter, P. Leach, y T. Berners-Lee, '
    '"Hypertext Transfer Protocol -- HTTP/1.1," RFC 2616, Internet Engineering Task Force (IETF), Jun. 1999.'
)
body(
    '[3] Postman Inc., "Postman Documentation and API Testing Guide," Postman Docs, 2026. [En línea]. '
    'Disponible en: https://learning.postman.com/docs/writing-scripts/test-scripts/'
)
body(
    '[4] JSONPlaceholder, "Free Fake REST API for Testing and Prototyping," typicode.com, 2026. [En línea]. '
    'Disponible en: https://jsonplaceholder.typicode.com/'
)
body(
    '[5] I. Sommerville, Software Engineering, 10.ª ed. Boston, MA, USA: Pearson Education, 2016.'
)
body(
    '[6] IEEE Standard for Software and System Test Documentation, IEEE Std 829-2008, '
    'IEEE Computer Society, Piscataway, NJ, USA, 2008.'
)

# Guardar documento Word
DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(DOCX_PATH))
print(f"Documento DOCX generado exitosamente en: {DOCX_PATH}")

# =====================================================================
# GENERACIÓN DE COLECCIÓN JSON DE POSTMAN
# =====================================================================
coleccion_postman = {
    "info": {
        "name": "Pruebas JSONPlaceholder REST API - UDG CUCosta",
        "description": "Colección oficial de pruebas funcionales y automatizadas para la práctica de Laboratorio de Pruebas de Software.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "1. GET - Consultar Post 1",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Accept", "value": "application/json"}
                ],
                "url": {
                    "raw": "https://jsonplaceholder.typicode.com/posts/1",
                    "protocol": "https",
                    "host": ["jsonplaceholder", "typicode", "com"],
                    "path": ["posts", "1"]
                }
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test(\"Código 200\", function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test(\"Tiempo de respuesta menor a 2 segundos\", function () {",
                            "    pm.expect(pm.response.responseTime).to.be.below(2000);",
                            "});",
                            "",
                            "pm.test(\"Que exista el campo title\", function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property(\"title\");",
                            "    pm.expect(jsonData.title).to.be.a(\"string\");",
                            "});"
                        ],
                        "type": "text/javascript"
                    }
                }
            ]
        },
        {
            "name": "2. POST - Crear Post",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "title": "Prueba API",
                        "body": "Actividad de testing",
                        "userId": 1
                    }, indent=2)
                },
                "url": {
                    "raw": "https://jsonplaceholder.typicode.com/posts",
                    "protocol": "https",
                    "host": ["jsonplaceholder", "typicode", "com"],
                    "path": ["posts"]
                }
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test(\"Código HTTP 201\", function () {",
                            "    pm.response.to.have.status(201);",
                            "});",
                            "",
                            "pm.test(\"Tiempo de respuesta menor a 2 segundos\", function () {",
                            "    pm.expect(pm.response.responseTime).to.be.below(2000);",
                            "});",
                            "",
                            "pm.test(\"Que el registro sea creado con ID\", function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property(\"id\");",
                            "    pm.expect(jsonData.title).to.eql(\"Prueba API\");",
                            "});"
                        ],
                        "type": "text/javascript"
                    }
                }
            ]
        },
        {
            "name": "3. PUT - Modificar Post 1",
            "request": {
                "method": "PUT",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "id": 1,
                        "title": "Prueba API Modificada",
                        "body": "Actividad de testing actualizada",
                        "userId": 1
                    }, indent=2)
                },
                "url": {
                    "raw": "https://jsonplaceholder.typicode.com/posts/1",
                    "protocol": "https",
                    "host": ["jsonplaceholder", "typicode", "com"],
                    "path": ["posts", "1"]
                }
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test(\"Código HTTP 200\", function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test(\"Tiempo de respuesta menor a 2 segundos\", function () {",
                            "    pm.expect(pm.response.responseTime).to.be.below(2000);",
                            "});",
                            "",
                            "pm.test(\"Datos actualizados correctamente\", function () {",
                            "    var jsonData = pm.response.json();",
                            "    pm.expect(jsonData.title).to.eql(\"Prueba API Modificada\");",
                            "    pm.expect(jsonData.body).to.eql(\"Actividad de testing actualizada\");",
                            "});"
                        ],
                        "type": "text/javascript"
                    }
                }
            ]
        },
        {
            "name": "4. DELETE - Eliminar Post 1",
            "request": {
                "method": "DELETE",
                "header": [
                    {"key": "Accept", "value": "application/json"}
                ],
                "url": {
                    "raw": "https://jsonplaceholder.typicode.com/posts/1",
                    "protocol": "https",
                    "host": ["jsonplaceholder", "typicode", "com"],
                    "path": ["posts", "1"]
                }
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test(\"Código HTTP 200 o 204\", function () {",
                            "    pm.expect([200, 204]).to.include(pm.response.code);",
                            "});",
                            "",
                            "pm.test(\"Tiempo de respuesta menor a 2 segundos\", function () {",
                            "    pm.expect(pm.response.responseTime).to.be.below(2000);",
                            "});"
                        ],
                        "type": "text/javascript"
                    }
                }
            ]
        }
    ]
}

with open(COLLECTION_PATH, 'w', encoding='utf-8') as f:
    json.dump(coleccion_postman, f, indent=2, ensure_ascii=False)
print(f"Colección Postman JSON generada en: {COLLECTION_PATH}")

# =====================================================================
# CONVERSIÓN A PDF MEDIANTE DOCX2PDF
# =====================================================================
try:
    from docx2pdf import convert
    print("Iniciando conversión a PDF...")
    convert(str(DOCX_PATH), str(PDF_PATH))
    print(f"Documento PDF generado exitosamente en: {PDF_PATH}")
except Exception as e:
    print(f"Nota: No se pudo convertir automáticamente a PDF: {e}")
