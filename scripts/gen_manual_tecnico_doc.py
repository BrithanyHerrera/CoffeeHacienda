"""
Generador del Documento Word y PDF del Manual Técnico y de Mantenimiento
Sistema: Coffee Hacienda POS
Universidad de Guadalajara - Centro Universitario de la Costa

Genera:
- c:\\CoffeeHacienda\\docs\\MANUAL_TECNICO.docx
- c:\\CoffeeHacienda\\docs\\MANUAL_TECNICO.pdf
"""

import os
import re
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# ==============================================================================
# CONFIGURACIÓN DE RUTAS Y CONSTANTES DE DISEÑO
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / 'docs'
DOCX_PATH = DOCS_DIR / 'MANUAL_TECNICO.docx'
PDF_PATH = DOCS_DIR / 'MANUAL_TECNICO.pdf'
LOGO_UDG_PATH = BASE_DIR / 'docs' / 'academico' / 'logo_udg.png'
LOGO_COFFEE_PATH = BASE_DIR / 'static' / 'images' / 'logo' / 'Logo Coffee Hacienda.png'

# Paleta Cromática Técnica
COLOR_PRIMARY_NAVY = RGBColor(27, 54, 93)     # #1B365D - Azul Institucional / Técnico
COLOR_SECONDARY_BLUE = RGBColor(43, 76, 126)  # #2B4C7E - Azul Pizarra Encabezados
COLOR_DARK_GRAY = RGBColor(55, 65, 81)        # #374151 - Gris Encabezados Menores
COLOR_TEXT_MAIN = RGBColor(31, 41, 55)        # #1F2937 - Carbón suave para lectura
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)    # #64748B - Gris pie / metadatos
COLOR_CODE_TEXT = RGBColor(15, 23, 42)        # #0F172A - Monospace texto
HEX_TABLE_HEADER_BG = "1B365D"                # Azul Marino para encabezados de tabla
HEX_TABLE_ZEBRA_BG = "F8FAFC"                 # Alternancia sutil de filas
HEX_CODE_BG = "F1F5F9"                        # Fondo gris suave para código
HEX_BORDER_LIGHT = "CBD5E1"                   # Borde de tablas

FONT_FAMILY = "Calibri"
FONT_CODE = "Consolas"

# ==============================================================================
# INICIALIZACIÓN DEL DOCUMENTO Y MÁRGENES
# ==============================================================================
doc = Document()

# Configurar márgenes de 2.5 cm en todas las secciones
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)  # Formato A4
    section.different_first_page_header_footer = True

# Ancho imprimible útil (21.0 - 5.0) = 16.0 cm
USABLE_WIDTH_CM = 16.0

# ==============================================================================
# UTILIDADES XML PARA FORMATO AVANZADO
# ==============================================================================
def set_cell_background(cell, fill_hex):
    """Aplica sombreado de fondo en formato hexadecimal a una celda."""
    tcPr = cell._tc.get_or_add_tcPr()
    # Eliminar sombreado anterior si existiera
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=70, bottom=70, left=90, right=90):
    """Define márgenes internos (padding) de la celda en dxa (1 pt = 20 dxa)."""
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

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    """Configura los bordes individuales de una celda mediante XML."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for edge, spec in borders.items():
        if spec:
            val = spec.get('val', 'single')
            sz = spec.get('sz', '4')
            color = spec.get('color', HEX_BORDER_LIGHT)
            tag = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>')
            tcBorders.append(tag)
        else:
            tag = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="nil"/>')
            tcBorders.append(tag)
    tcPr.append(tcBorders)

def prevent_row_split(row):
    """Evita que una fila de tabla se parta a mitad de página."""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_repeat_table_header(row):
    """Marca la primera fila de una tabla para repetirse en saltos de página."""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

# ==============================================================================
# CONFIGURACIÓN DE ENCABEZADOS Y PIES DE PÁGINA
# ==============================================================================
subsequent_section = doc.sections[0]

# Encabezado (Páginas 2 en adelante)
header = subsequent_section.header
header_p = header.paragraphs[0]
header_p.text = ""
header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
header_p.paragraph_format.space_after = Pt(4)
r_head = header_p.add_run("Coffee Hacienda POS — Manual Técnico y de Mantenimiento")
r_head.font.name = FONT_FAMILY
r_head.font.size = Pt(8.5)
r_head.font.color.rgb = COLOR_TEXT_MUTED

# Pie de página (Páginas 2 en adelante)
footer = subsequent_section.footer
footer_p = footer.paragraphs[0]
footer_p.text = ""
footer_p.paragraph_format.space_before = Pt(4)

# Usamos una tabla de 1 fila x 2 columnas para alinear perfectamente izquierda y derecha
tbl_footer = footer.add_table(rows=1, cols=2, width=Cm(USABLE_WIDTH_CM))
tbl_footer.alignment = WD_TABLE_ALIGNMENT.CENTER
row_ft = tbl_footer.rows[0]

# Celda Izquierda: Estado confidencial
cell_left = row_ft.cells[0]
cell_left.width = Cm(10.0)
p_left = cell_left.paragraphs[0]
p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
p_left.paragraph_format.space_before = Pt(0)
p_left.paragraph_format.space_after = Pt(0)
r_conf = p_left.add_run("Confidencial / Uso Técnico y de Mantenimiento Interno")
r_conf.font.name = FONT_FAMILY
r_conf.font.size = Pt(8.5)
r_conf.font.color.rgb = COLOR_TEXT_MUTED

# Celda Derecha: Numeración de página dinámica
cell_right = row_ft.cells[1]
cell_right.width = Cm(6.0)
p_right = cell_right.paragraphs[0]
p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
p_right.paragraph_format.space_before = Pt(0)
p_right.paragraph_format.space_after = Pt(0)

r_pg1 = p_right.add_run("Página ")
r_pg1.font.name = FONT_FAMILY
r_pg1.font.size = Pt(8.5)
r_pg1.font.color.rgb = COLOR_TEXT_MUTED

r_page_field = p_right.add_run()
r_page_field.font.name = FONT_FAMILY
r_page_field.font.size = Pt(8.5)
r_page_field.font.color.rgb = COLOR_TEXT_MUTED
fld_page = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
r_page_field._r.append(fld_page)

r_pg2 = p_right.add_run(" de ")
r_pg2.font.name = FONT_FAMILY
r_pg2.font.size = Pt(8.5)
r_pg2.font.color.rgb = COLOR_TEXT_MUTED

r_numpages_field = p_right.add_run()
r_numpages_field.font.name = FONT_FAMILY
r_numpages_field.font.size = Pt(8.5)
r_numpages_field.font.color.rgb = COLOR_TEXT_MUTED
fld_numpages = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="NUMPAGES"/>')
r_numpages_field._r.append(fld_numpages)

for c in row_ft.cells:
    set_cell_borders(c)
    set_cell_margins(c, top=0, bottom=0, left=0, right=0)

# ==============================================================================
# COMPONENTES DE TIPOGRAFÍA Y FORMATO
# ==============================================================================
def add_heading_1(text):
    """Encabezado de Nivel 1 estilizado."""
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.bold = True
    r.font.name = FONT_FAMILY
    r.font.size = Pt(15.0)
    r.font.color.rgb = COLOR_PRIMARY_NAVY
    return p

def add_heading_2(text):
    """Encabezado de Nivel 2 estilizado."""
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.bold = True
    r.font.name = FONT_FAMILY
    r.font.size = Pt(12.5)
    r.font.color.rgb = COLOR_SECONDARY_BLUE
    return p

def add_heading_3(text):
    """Encabezado de Nivel 3 estilizado."""
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.bold = True
    r.font.name = FONT_FAMILY
    r.font.size = Pt(11.0)
    r.font.color.rgb = COLOR_DARK_GRAY
    return p

def add_formatted_runs(paragraph, text, base_size=10.5, base_color=COLOR_TEXT_MAIN):
    """Parsea texto con soporte para negrita (**bold**) y código (`code`)."""
    pattern = re.compile(r'(\*\*.*?\*\*|`.*?`)')
    tokens = pattern.split(text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**') and len(token) >= 4:
            r = paragraph.add_run(token[2:-2])
            r.bold = True
            r.font.name = FONT_FAMILY
            r.font.size = Pt(base_size)
            r.font.color.rgb = base_color
        elif token.startswith('`') and token.endswith('`') and len(token) >= 2:
            r = paragraph.add_run(token[1:-1])
            r.font.name = FONT_CODE
            r.font.size = Pt(base_size - 0.5)
            r.font.color.rgb = RGBColor(30, 41, 59)
        else:
            r = paragraph.add_run(token)
            r.font.name = FONT_FAMILY
            r.font.size = Pt(base_size)
            r.font.color.rgb = base_color

def add_body(text, space_after=4, justify=True):
    """Párrafo de cuerpo de texto con interlineado 1.15."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_formatted_runs(p, text)
    return p

def add_bullet(bold_prefix, text):
    """Elemento de lista con viñeta y prefijo en negrita."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    clean_prefix = bold_prefix.strip()
    if clean_prefix:
        r_pre = p.add_run(clean_prefix + " ")
        r_pre.bold = True
        r_pre.font.name = FONT_FAMILY
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = COLOR_TEXT_MAIN
    
    add_formatted_runs(p, text)
    return p

def add_code_block(code_content, language="bash"):
    """Bloque de código estilizado con fondo suave y borde izquierdo."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(USABLE_WIDTH_CM)
    
    set_cell_background(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=70, bottom=70, left=120, right=90)
    set_cell_borders(
        cell,
        left={'val': 'single', 'sz': '24', 'color': '64748B'},
        top={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
        right={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
        bottom={'val': 'single', 'sz': '4', 'color': 'E2E8F0'}
    )
    prevent_row_split(tbl.rows[0])
    
    lines = code_content.strip().split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.05
        
        r = p.add_run(line)
        r.font.name = FONT_CODE
        r.font.size = Pt(9.0)
        r.font.color.rgb = COLOR_CODE_TEXT

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)

def add_alert_box(alert_type, title, text):
    """Caja de alerta profesional (> [!CAUTION], > [!IMPORTANT], > [!TIP], > [!NOTE])."""
    type_configs = {
        'caution': {
            'border_color': 'DC2626',
            'bg_color': 'FEF2F2',
            'title_color': RGBColor(153, 27, 27),
            'text_color': RGBColor(127, 29, 29),
            'default_title': 'ADVERTENCIA CRÍTICA — SEGURIDAD'
        },
        'important': {
            'border_color': 'D97706',
            'bg_color': 'FFFBEB',
            'title_color': RGBColor(146, 64, 14),
            'text_color': RGBColor(120, 53, 15),
            'default_title': 'AVISO IMPORTANTE DE OPERACIÓN'
        },
        'tip': {
            'border_color': '16A34A',
            'bg_color': 'F0FDF4',
            'title_color': RGBColor(22, 101, 52),
            'text_color': RGBColor(20, 83, 45),
            'default_title': 'CONSEJO DE DESARROLLO Y ENTORNO'
        },
        'note': {
            'border_color': '2563EB',
            'bg_color': 'EFF6FF',
            'title_color': RGBColor(30, 64, 175),
            'text_color': RGBColor(30, 58, 138),
            'default_title': 'NOTA TÉCNICA DEL SISTEMA'
        }
    }
    
    cfg = type_configs.get(alert_type.lower(), type_configs['note'])
    
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(USABLE_WIDTH_CM)
    
    set_cell_background(cell, cfg['bg_color'])
    set_cell_margins(cell, top=80, bottom=80, left=130, right=90)
    set_cell_borders(
        cell,
        left={'val': 'single', 'sz': '28', 'color': cfg['border_color']},
        top={'val': 'single', 'sz': '4', 'color': cfg['border_color']},
        right={'val': 'single', 'sz': '4', 'color': cfg['border_color']},
        bottom={'val': 'single', 'sz': '4', 'color': cfg['border_color']}
    )
    prevent_row_split(tbl.rows[0])
    
    # Título de la alerta
    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    p_title.paragraph_format.line_spacing = 1.1
    r_t = p_title.add_run(f"[{title or cfg['default_title']}]")
    r_t.bold = True
    r_t.font.name = FONT_FAMILY
    r_t.font.size = Pt(10.0)
    r_t.font.color.rgb = cfg['title_color']
    
    # Texto de la alerta
    p_text = cell.add_paragraph()
    p_text.paragraph_format.space_before = Pt(0)
    p_text.paragraph_format.space_after = Pt(0)
    p_text.paragraph_format.line_spacing = 1.15
    p_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_formatted_runs(p_text, text, base_size=9.5, base_color=cfg['text_color'])
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)

def add_styled_table(headers, data_rows, col_widths, alignments=None):
    """Crea una tabla profesional con encabezados coloreados, bordes y zebra shading."""
    tbl = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    
    # Fila de Encabezado
    hdr_row = tbl.rows[0]
    set_repeat_table_header(hdr_row)
    prevent_row_split(hdr_row)
    
    for j, h_text in enumerate(headers):
        cell = hdr_row.cells[j]
        cell.width = Cm(col_widths[j])
        set_cell_background(cell, HEX_TABLE_HEADER_BG)
        set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
        set_cell_borders(
            cell,
            top={'val': 'single', 'sz': '6', 'color': '1B365D'},
            bottom={'val': 'single', 'sz': '12', 'color': '0F172A'},
            left={'val': 'single', 'sz': '4', 'color': '334155'},
            right={'val': 'single', 'sz': '4', 'color': '334155'}
        )
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.1
        
        align = WD_ALIGN_PARAGRAPH.CENTER
        if alignments and j < len(alignments):
            align = alignments[j]
        p.alignment = align
        
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = FONT_FAMILY
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    # Filas de Datos
    for i, row_data in enumerate(data_rows):
        row = tbl.rows[i + 1]
        prevent_row_split(row)
        bg_color = HEX_TABLE_ZEBRA_BG if (i % 2 == 1) else "FFFFFF"
        
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            cell.width = Cm(col_widths[j])
            if bg_color != "FFFFFF":
                set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            set_cell_borders(
                cell,
                top={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
                bottom={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
                left={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
                right={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT}
            )
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            
            align = WD_ALIGN_PARAGRAPH.LEFT
            if alignments and j < len(alignments):
                align = alignments[j]
            p.alignment = align
            
            add_formatted_runs(p, str(val), base_size=9.0)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)
    return tbl

# ==============================================================================
# CONSTRUCCIÓN DE LA PORTADA
# ==============================================================================
print("Construyendo Portada Institucional y Técnica...")

p_cov_space = doc.add_paragraph()
p_cov_space.paragraph_format.space_before = Pt(10)

# Encabezado Institucional Universitario
p_inst = doc.add_paragraph()
p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_inst.paragraph_format.space_after = Pt(2)
r_inst1 = p_inst.add_run("UNIVERSIDAD DE GUADALAJARA\n")
r_inst1.bold = True
r_inst1.font.name = FONT_FAMILY
r_inst1.font.size = Pt(14)
r_inst1.font.color.rgb = COLOR_PRIMARY_NAVY

r_inst2 = p_inst.add_run("CENTRO UNIVERSITARIO DE LA COSTA\n")
r_inst2.bold = True
r_inst2.font.name = FONT_FAMILY
r_inst2.font.size = Pt(12)
r_inst2.font.color.rgb = COLOR_SECONDARY_BLUE

r_inst3 = p_inst.add_run("DIVISIÓN DE INGENIERÍAS Y CIENCIAS EXACTAS")
r_inst3.font.name = FONT_FAMILY
r_inst3.font.size = Pt(10)
r_inst3.font.color.rgb = COLOR_DARK_GRAY

# Logotipo UDG
if LOGO_UDG_PATH.exists():
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(8)
    p_logo.paragraph_format.space_after = Pt(8)
    p_logo.add_run().add_picture(str(LOGO_UDG_PATH), width=Cm(3.2))

# Bloque de Título Principal del Documento
p_badge = doc.add_paragraph()
p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_badge.paragraph_format.space_before = Pt(6)
p_badge.paragraph_format.space_after = Pt(2)
r_b = p_badge.add_run("DOCUMENTO DE ARQUITECTURA, DESPLIEGUE Y OPERACIONES")
r_b.bold = True
r_b.font.name = FONT_FAMILY
r_b.font.size = Pt(9.5)
r_b.font.color.rgb = RGBColor(37, 99, 235)

p_tit = doc.add_paragraph()
p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_tit.paragraph_format.space_before = Pt(2)
p_tit.paragraph_format.space_after = Pt(4)
r_tit = p_tit.add_run("Manual Técnico y de Mantenimiento")
r_tit.bold = True
r_tit.font.name = FONT_FAMILY
r_tit.font.size = Pt(22)
r_tit.font.color.rgb = COLOR_PRIMARY_NAVY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_before = Pt(0)
p_sub.paragraph_format.space_after = Pt(14)
r_sub = p_sub.add_run("Coffee Hacienda POS — Sistema de Punto de Venta y Gestión Comercial")
r_sub.font.name = FONT_FAMILY
r_sub.font.size = Pt(13)
r_sub.font.color.rgb = COLOR_SECONDARY_BLUE

# Cuadro Técnico de Ficha del Documento
tbl_meta = doc.add_table(rows=8, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_meta.style = 'Table Grid'

meta_data = [
    ("Sistema:", "Coffee Hacienda POS"),
    ("Versión del Documento:", "1.0 (Producción)"),
    ("Fecha de Emisión:", "Noviembre 2026"),
    ("Audiencia Destinataria:", "Desarrolladores, Administradores de Sistemas y Personal de Mantenimiento"),
    ("Arquitectura Base:", "Python 3.12+ | Flask 3.0+ | MySQL 8.0+ Dual (Local / Aiven TLS)"),
    ("Cobertura de Calidad:", "323 Pruebas Automatizadas Pasadas (328 Totales, 0 Fallos)"),
    ("Control de Versiones:", "Git | Rama: feat/mejoras-operativas-pos"),
    ("Equipo de Desarrollo:", "Corona Méndez Jonathan Ismael\nGonzález Crisanto Ana Karen\nHerrera Galindo Brithany Juliette")
]

for idx, (label, val) in enumerate(meta_data):
    row = tbl_meta.rows[idx]
    prevent_row_split(row)
    
    c_lbl = row.cells[0]
    c_lbl.width = Cm(5.0)
    set_cell_background(c_lbl, "F8FAFC")
    set_cell_margins(c_lbl, top=45, bottom=45, left=70, right=70)
    set_cell_borders(
        c_lbl,
        top={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
        bottom={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
        left={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
        right={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT}
    )
    p_lbl = c_lbl.paragraphs[0]
    p_lbl.paragraph_format.space_before = Pt(1)
    p_lbl.paragraph_format.space_after = Pt(1)
    r_l = p_lbl.add_run(label)
    r_l.bold = True
    r_l.font.name = FONT_FAMILY
    r_l.font.size = Pt(9.5)
    r_l.font.color.rgb = COLOR_PRIMARY_NAVY
    
    c_val = row.cells[1]
    c_val.width = Cm(11.0)
    set_cell_background(c_val, "FFFFFF")
    set_cell_margins(c_val, top=45, bottom=45, left=70, right=70)
    set_cell_borders(
        c_val,
        top={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
        bottom={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
        left={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT},
        right={'val': 'single', 'sz': '4', 'color': HEX_BORDER_LIGHT}
    )
    p_val = c_val.paragraphs[0]
    p_val.paragraph_format.space_before = Pt(1)
    p_val.paragraph_format.space_after = Pt(1)
    r_v = p_val.add_run(val)
    r_v.font.name = FONT_FAMILY
    r_v.font.size = Pt(9.5)
    r_v.font.color.rgb = COLOR_TEXT_MAIN

p_pie_port = doc.add_paragraph()
p_pie_port.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_pie_port.paragraph_format.space_before = Pt(20)
r_pp = p_pie_port.add_run("Puerto Vallarta, Jalisco — Noviembre 2026")
r_pp.font.name = FONT_FAMILY
r_pp.font.size = Pt(9.5)
r_pp.font.color.rgb = COLOR_TEXT_MUTED

doc.add_page_break()

# ==============================================================================
# TABLA DE CONTENIDOS
# ==============================================================================
print("Generando Tabla de Contenidos estructurada...")

add_heading_1("📖 Tabla de Contenidos del Manual")
add_body(
    "El presente manual constituye la guía de referencia técnica oficial para el desarrollo, "
    "despliegue, aseguramiento de calidad y mantenimiento operativo de **Coffee Hacienda POS**. "
    "A continuación se detalla la estructura temática:"
)

toc_items = [
    ("Introducción y Stack Tecnológico", "Fundamentos del patrón Application Factory, arquitectura desacoplada y tabla de tecnologías."),
    ("1. Requisitos del Sistema", "Especificaciones de hardware, versiones de intérpretes, navegadores y servidores."),
    ("2. Instalación Inicial Paso a Paso", "Flujo ordenado en 8 pasos para clonar, preparar entorno virtual, migrar base de datos y correr."),
    ("3. Configuración de Variables de Entorno (bd.env)", "Matriz técnica exhaustiva de los 17 parámetros de configuración y políticas de seguridad."),
    ("4. Arquitectura del Software", "Desacoplamiento de dominios, Application Factory y desglose del árbol de directorios del proyecto."),
    ("5. Base de Datos y Entorno Dual MySQL", "Conexión local y nube TLS en Aiven, catálogo integral de las 22 tablas y sistema de migraciones."),
    ("6. Pool de Conexiones (bd.py)", "Implementación de DBUtils PooledDB, gestión de reconexiones automáticas (ping=4) y mejores prácticas."),
    ("7. Seguridad, Autenticación y Autorización", "Decoradores @login_required y @admin_required, prevención de SQLi, CSRF y mitigación de fuerza bruta."),
    ("8. Catálogo de Blueprints y Rutas API", "Catálogo exhaustivo de endpoints agrupados en los 7 blueprints modulares del sistema."),
    ("9. Suite de Pruebas Automatizadas (pytest)", "Comandos de ejecución, métricas de calidad (323 tests superados) y análisis estático con Ruff."),
    ("10. Gestión y Almacenamiento de Archivos", "Matriz de resguardo de tickets PDF, imágenes de catálogo y generación de comprobantes en memoria."),
    ("11. Despliegue en Producción y Nube (Aiven)", "Pautas para servidores WSGI (Waitress en Windows / Gunicorn en Linux) y TLS en Aiven."),
    ("12. Control de Versiones y Flujo Git", "Convención de commits semánticos, políticas de branching y sincronización de código."),
    ("13. Directrices para Agentes de IA (AGENTS.md)", "Reglas no negociables: inmutabilidad de ventas, corte continuo, auditoría y parametrización."),
    ("14. Guía de Solución de Problemas (Troubleshooting)", "Diagnósticos rápidos ante caídas de conexión a base de datos, fallos SSL, errores CSRF y pytest.")
]

for idx, (title, desc) in enumerate(toc_items):
    add_bullet(f"{idx + 1}. {title}:", desc)

doc.add_page_break()

# ==============================================================================
# SECCIÓN 1: INTRODUCCIÓN Y STACK TECNOLÓGICO
# ==============================================================================
print("Redactando Sección: Introducción y Stack Tecnológico...")

add_heading_1("🚀 Introducción y Stack Tecnológico")
add_body(
    "**Coffee Hacienda POS** es una aplicación web empresarial orientada a la gestión operativa, comercial "
    "y contable de cafeterías y establecimientos gastronómicos. Diseñada con un enfoque modular y arquitectura "
    "desacoplada, implementa el patrón de diseño **Application Factory** de Flask en conjunto con separación de "
    "dominios funcionales mediante **Blueprints**."
)
add_body(
    "La arquitectura garantiza una estricta separación de responsabilidades: los controladores gestionan las "
    "peticiones HTTP y validaciones, la capa de modelos ejecuta consultas SQL 100% parametrizadas a través "
    "de un pool de conexiones reutilizables, y la interfaz gráfica combina renderizado del lado del servidor (SSR) "
    "con componentes reactivos en JavaScript Vanilla para una experiencia de usuario fluida y de baja latencia."
)

add_heading_2("Componentes del Stack Tecnológico")

stack_headers = ["Capa de Software", "Tecnología Seleccionada", "Propósito en la Arquitectura"]
stack_widths = [3.4, 4.6, 8.0]
stack_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]

stack_data = [
    ["**Lenguaje Backend**", "Python 3.12+", "Lógica de negocio, controladores de dominio y orquestación de endpoints"],
    ["**Framework Web**", "Flask 3.0+", "Enrutamiento HTTP, renderizado de plantillas Jinja2 y serialización REST"],
    ["**Motor de Base de Datos**", "MySQL 8.0+ / MAMP / Aiven", "Persistencia relacional y transacciones con aislamiento ACID"],
    ["**Pool de Conexiones**", "DBUtils (PooledDB) + PyMySQL", "Reutilización eficiente de sockets de conexión de alto rendimiento"],
    ["**Seguridad Web**", "Flask-WTF (CSRF) + Flask-Limiter", "Protección contra falsificación de peticiones y mitigación de DoS/fuerza bruta"],
    ["**Criptografía y Sesión**", "Werkzeug Security", "Hashing de contraseñas mediante algoritmo PBKDF2:SHA256"],
    ["**Plantillas Dinámicas**", "Jinja2 + HTML5 semántico", "Renderizado del lado del servidor (SSR) y escape seguro de variables"],
    ["**Frontend UI**", "Bootstrap 5 + Vanilla JavaScript", "Interfaz responsiva, modales interactivos y peticiones asíncronas fetch()"],
    ["**Generación de PDFs**", "jsPDF + AutoTable", "Construcción silenciosa de tickets de venta y comprobantes de corte"],
    ["**Servicio de Correo**", "Flask-Mail (SMTP / STARTTLS)", "Notificaciones y envío de tokens temporales de recuperación de acceso"],
    ["**Pruebas y Calidad**", "pytest + Ruff", "Suite de 328 pruebas automatizadas y linter de cumplimiento PEP8"]
]

add_styled_table(stack_headers, stack_data, stack_widths, stack_align)

# ==============================================================================
# SECCIÓN 2: REQUISITOS DEL SISTEMA
# ==============================================================================
print("Redactando Sección: Requisitos del Sistema...")

add_heading_1("1. Requisitos del Sistema")
add_body(
    "Para garantizar un rendimiento óptimo tanto en estaciones de cobro locales como en entornos de servidor "
    "y contenedores en la nube, se establecen los siguientes requerimientos de infraestructura:"
)

add_heading_2("1.1 Entorno de Desarrollo y Servidor Local")

req_headers = ["Componente", "Requisito Mínimo", "Configuración Recomendada"]
req_widths = [3.5, 6.5, 6.0]
req_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]

req_data = [
    ["**Sistema Operativo**", "Windows 10/11, macOS 12+, Ubuntu 22.04 LTS", "Windows 11 x64 / Linux Server 22.04+"],
    ["**Intérprete Python**", "Python 3.12.0 x64", "Python 3.12.4 o superior"],
    ["**Servidor MySQL**", "MySQL 5.7+ o MariaDB 10.4+", "MySQL 8.0 Community Server o MAMP Pro"],
    ["**Memoria RAM**", "4 GB de memoria física", "8 GB o superior (recomendado 16 GB)"],
    ["**Almacenamiento**", "2 GB de espacio libre en disco", "Unidad de estado sólido (SSD) con 10 GB libres"],
    ["**Navegador Web**", "Google Chrome 110+, Edge 110+, Firefox 115+", "Google Chrome / Microsoft Edge última versión"]
]

add_styled_table(req_headers, req_data, req_widths, req_align)

# ==============================================================================
# SECCIÓN 3: INSTALACIÓN INICIAL PASO A PASO
# ==============================================================================
print("Redactando Sección: Instalación Inicial Paso a Paso...")

add_heading_1("2. Instalación Inicial Paso a Paso")
add_body(
    "Siga este procedimiento detallado para desplegar el entorno de desarrollo y pruebas locales desde "
    "cero en una estación de trabajo con Windows:"
)

add_heading_2("Paso 1: Clonar el Repositorio de Código")
add_body("Obtenga el código fuente del proyecto mediante Git desde la terminal:")
add_code_block(
    "git clone https://github.com/BrithanyHerrera/CoffeeHacienda.git\n"
    "cd CoffeeHacienda"
)

add_heading_2("Paso 2: Crear el Entorno Virtual de Python")
add_body("Genere un entorno virtual aislado para evitar colisiones con paquetes globales del sistema:")
add_code_block("python -m venv .venv")

add_heading_2("Paso 3: Activar el Entorno Virtual")
add_body("Active el entorno según el intérprete de comandos utilizado:")
add_code_block(
    "# En Windows PowerShell:\n"
    ".\\.venv\\Scripts\\Activate.ps1\n\n"
    "# En Windows CMD tradicional:\n"
    ".\\.venv\\Scripts\\activate.bat"
)
add_alert_box(
    "tip",
    "DETECCIÓN AUTOMÁTICA EN APP.PY",
    "El punto de entrada `app.py` incluye detección y auto-relanzamiento transparente: si un desarrollador "
    "lo ejecuta invocando el Python global de Windows, el script detecta automáticamente la existencia "
    "de `.venv/Scripts/python.exe` y se re-ejecuta dentro de dicho entorno virtual sin requerir intervención manual."
)

add_heading_2("Paso 4: Instalar las Dependencias de Software")
add_body("Actualice el gestor de paquetes pip e instale los requerimientos del proyecto:")
add_code_block(
    "python -m pip install --upgrade pip\n"
    "pip install -r requirements-dev.txt"
)
add_body("*(Nota: En estaciones de caja que no requieran correr suites de pruebas unitarias, basta instalar `requirements.txt`).*")

add_heading_2("Paso 5: Configurar el Archivo de Entorno (bd.env)")
add_body("Copie la plantilla de variables públicas e inicialice el archivo local:")
add_code_block("copy bd.env.example bd.env")
add_body("Abra `bd.env` en su editor de código y configure sus credenciales locales de base de datos y clave secreta.")

add_heading_2("Paso 6: Configurar e Inicializar la Base de Datos Local")
add_body(
    "1. Inicie su motor local de MySQL (por ejemplo mediante MAMP o el servicio de Windows), verificando que el puerto `3306` esté abierto.\n"
    "2. Abra la consola de comandos de MySQL o phpMyAdmin y cree la base de datos con codificación UTF-8 Multibyte:"
)
add_code_block("CREATE DATABASE bd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
add_body("3. Importe el esquema base relacional:")
add_code_block("mysql -u root -p bd < database/db.sql")

add_heading_2("Paso 7: Crear el Primer Usuario Administrador")
add_body("Ejecute el script de aprovisionamiento de superusuarios provisto en el sistema:")
add_code_block("python scripts/create_admin.py --username admin --email admin@coffeehacienda.com")
add_body("El script solicitará por teclado la contraseña segura, aplicando hashing con sal criptográfica Werkzeug.")

add_heading_2("Paso 8: Iniciar el Servidor de Desarrollo")
add_body("Inicie la aplicación mediante consola o ejecutando el archivo por lotes `iniciar_sistema.bat`:")
add_code_block("python app.py")
add_body("Acceda a la plataforma desde su navegador en: **`http://127.0.0.1:5000`**")

# ==============================================================================
# SECCIÓN 4: VARIABLES DE ENTORNO (BD.ENV)
# ==============================================================================
print("Redactando Sección: Variables de Entorno (bd.env)...")

add_heading_1("3. Configuración de Variables de Entorno (bd.env)")
add_body(
    "La configuración operacional y de seguridad del sistema se parametriza mediante el archivo `bd.env`. "
    "Este archivo contiene credenciales críticas de bases de datos, llaves de sesión y accesos de correo."
)

add_alert_box(
    "caution",
    "CONFIDENCIALIDAD DE SECRETOS Y REGLAS DE VERSIONADO",
    "El archivo `bd.env` contiene secretos reales de producción y pruebas. **Bajo ninguna circunstancia debe subirse "
    "o versionarse en Git**. Se encuentra registrado en `.gitignore`. Cuando se agregue una nueva variable, documente "
    "su estructura en `bd.env.example` utilizando valores estrictamente ficticios."
)

add_heading_2("Matriz Completa de Variables de Configuración")

env_headers = ["Variable", "Tipo", "Descripción Funcional", "Valor Ejemplo / Defecto", "¿Req?"]
env_widths = [3.6, 1.6, 5.2, 4.2, 1.4]
env_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]

env_data = [
    ["`APP_ENV`", "String", "Entorno activo: `LOCAL`, `NUBE`, `PRODUCTION` o `TESTING`", "`LOCAL`", "Sí"],
    ["`SECRET_KEY`", "String", "Semilla criptográfica para firma de cookies y tokens CSRF", "Clave segura 64 caracteres", "Sí"],
    ["`FLASK_DEBUG`", "Boolean", "Debugger interactivo y recarga en caliente (desactivar en producción)", "`True` (local) / `False`", "Sí"],
    ["`MAX_CONTENT_LENGTH_MB`", "Integer", "Tope máximo en Megabytes para peticiones entrantes (ej. imágenes)", "`8`", "No"],
    ["`SESSION_VALIDATION_INTERVAL_SECONDS`", "Integer", "Frecuencia en segundos de re-validación de vigencia de usuario en BD", "`60`", "No"],
    ["`RATELIMIT_STORAGE_URI`", "URI", "Almacén de cuotas del Rate Limiter (`memory://` o `redis://`)", "`memory://` (local)", "Sí"],
    ["`TRUST_PROXY`", "Boolean", "Middleware ProxyFix para decodificar headers X-Forwarded detrás de Nginx", "`False` (local) / `True`", "Sí"],
    ["`DB_HOST`", "String", "Dirección IP o hostname del motor MySQL activo", "`127.0.0.1` / hostname Aiven", "Sí"],
    ["`DB_PORT`", "Integer", "Puerto de escucha del servicio MySQL", "`3306` (MAMP) / puerto TLS", "Sí"],
    ["`DB_USER`", "String", "Usuario con permisos de lectura/escritura en BD", "`root` / `avnadmin`", "Sí"],
    ["`DB_PASSWORD`", "String", "Contraseña del usuario de base de datos", "Contraseña de base de datos", "Sí"],
    ["`DB_NAME`", "String", "Nombre de la base de datos relacional activa", "`bd` / `defaultdb`", "Sí"],
    ["`DB_SSL_CA`", "FilePath", "Ruta absoluta al certificado CA (`.pem`) para cifrado TLS", "`C:/certificados/ca.pem`", "Solo Nube"],
    ["`MAIL_SERVER`", "String", "Servidor SMTP para envío transaccional de correos", "`smtp.gmail.com`", "Sí"],
    ["`MAIL_PORT`", "Integer", "Puerto de conexión al servidor SMTP", "`587` (STARTTLS)", "Sí"],
    ["`MAIL_USE_TLS`", "Boolean", "Habilita cifrado de transporte STARTTLS", "`True`", "Sí"],
    ["`MAIL_USERNAME`", "Email", "Cuenta de correo emisora de notificaciones", "`notificaciones@coffeehacienda.com`", "Sí"],
    ["`MAIL_PASSWORD`", "String", "Contraseña de aplicación generada para el correo", "`xxxx xxxx xxxx xxxx`", "Sí"]
]

add_styled_table(env_headers, env_data, env_widths, env_align)

# ==============================================================================
# SECCIÓN 5: ARQUITECTURA DEL SOFTWARE
# ==============================================================================
print("Redactando Sección: Arquitectura del Software...")

add_heading_1("4. Arquitectura del Software")
add_body(
    "El sistema implementa una arquitectura modular desacoplada fundamentada en el patrón **Application Factory**. "
    "A través de la función constructora `create_app(config_class)`, la aplicación inicializa de forma determinista "
    "las extensiones globales (`Flask-WTF`, `Flask-Limiter`, `Flask-Mail`), registra los manejadores de errores "
    "HTTP (400, 403, 404, 429, 500) y monta los 7 Blueprints funcionales que componen los dominios de la cafetería."
)

add_heading_2("4.1 Estructura Integral de Directorios")
add_body("A continuación se presenta el árbol de carpetas del repositorio de código con la función de cada elemento:")

tree_structure = """CoffeeHacienda/
├── app.py                      # Fábrica de aplicación (create_app) y punto de entrada
├── bd.py                       # Gestor del Pool de conexiones MySQL (DBUtils PooledDB)
├── config.py                   # Configuraciones por entorno (LocalConfig, ProductionConfig)
├── extensions.py               # Instancias compartidas (limiter, csrf, mail)
├── utils.py                    # Decoradores (@login_required, @admin_required) y utilidades
├── blueprints/                 # Controladores y rutas agrupados por dominio de negocio
│   ├── autenticacion_bp.py     # Login, logout, recuperación de contraseña
│   ├── finanzas_bp.py          # Cortes de caja, exportación Excel, reportes contables
│   ├── generales_bp.py         # Healthcheck, guardado de tickets PDF, bienvenida
│   ├── inventario_bp.py        # Control de existencias, ajustes con motivo obligatorio
│   ├── productos_bp.py         # Catálogo de productos, categorías, subida de imágenes
│   ├── usuarios_bp.py          # Administración de personal, altas, bajas, roles
│   └── ventas_bp.py            # POS Menú, pedidos, órdenes, historial y exportación
├── models/                     # Capa de acceso a datos y consultas SQL parametrizadas
│   ├── modelsCorteCaja.py
│   ├── modelsHistorial.py
│   ├── modelsInventario.py
│   ├── modelsOrdenes.py
│   ├── modelsProductos.py
│   ├── modelsReporteFinanciero.py
│   ├── modelsUsuarios.py
│   └── modelsVentas.py
├── templates/                  # Plantillas HTML renderizadas del lado del servidor (Jinja2)
│   ├── bienvenida.html
│   ├── corteCaja.html
│   ├── gestionProductos.html
│   ├── gestionUsuarios.html
│   ├── historial.html
│   ├── inventario.html
│   ├── login.html
│   ├── menu.html
│   ├── ordenes.html
│   ├── recuperar.html
│   └── reportesFinancieros.html
├── static/                     # Recursos estáticos de cliente
│   ├── css/                    # Hojas de estilo modulares por interfaz
│   ├── js/                     # Scripts clientes (menu.js, inventario.js, corteCaja.js)
│   └── images/productos/       # Imágenes de catálogo cargadas dinámicamente
├── database/                   # Definición de persistencia relacional
│   ├── db.sql                  # Esquema maestro completo de la base de datos
│   └── migraciones/            # Scripts SQL versionados secuencialmente (001_..., 002_...)
├── scripts/                    # Scripts de soporte administrativo y automatización
│   ├── apply_migrations.py     # Aplicador transaccional de migraciones pendientes
│   ├── create_admin.py         # Aprovisionamiento seguro de administradores vía CLI
│   └── gen_manual_tecnico_doc.py # Generador de este documento técnico en Word y PDF
├── tests/                      # Suite de pruebas automatizadas con pytest
│   ├── conftest.py             # Fixtures de aplicación cliente y simuladores
│   └── db_fakes.py             # Drivers y cursores falsos para pruebas unitarias sin BD real
├── instance/pdfs/              # Almacén local de comprobantes (ignorado en Git)
│   ├── tickets_ventas/         # Comprobantes de compra generados en caja
│   └── cortes_de_caja/         # Resguardos de arqueos continuos de caja
├── docs/                       # Documentación técnica y académica formal
│   ├── MANUAL_USUARIO.md       # Manual operativo para cajeros y administradores
│   └── MANUAL_TECNICO.md       # Especificación técnica viva del sistema
├── bd.env                      # Variables de entorno activas locales (gitignored)
├── bd.env.example              # Plantilla pública de variables requeridas
└── AGENTS.md                   # Directrices y reglas de negocio para agentes de IA"""

add_code_block(tree_structure, language="text")

# ==============================================================================
# SECCIÓN 6: BASE DE DATOS Y ENTORNO DUAL MYSQL
# ==============================================================================
print("Redactando Sección: Base de Datos y Entorno Dual...")

add_heading_1("5. Base de Datos y Entorno Dual MySQL")
add_body(
    "El sistema cuenta con soporte bidireccional transparente para dos modalidades de base de datos:\n"
    "1. **Entorno Local (Desarrollo / Offline):** MySQL en MAMP o servidor nativo (`127.0.0.1:3306`), base de datos `bd`.\n"
    "2. **Entorno Nube (Producción / Alta Disponibilidad):** Aiven MySQL Gestionado con conexión TLS mandatoria "
    "validada mediante certificado CA (`DB_SSL_CA`)."
)

add_heading_2("5.1 Catálogo de Tablas del Esquema Relacional")
add_body(
    "El esquema maestro relacional de Coffee Hacienda POS se compone de **22 tablas normalizadas**, diseñadas "
    "bajo principios de integridad referencial, índices en claves foráneas y trazabilidad inmutable:"
)

tbl_schema_headers = ["Tabla", "Propósito Funcional y Columnas Clave"]
tbl_schema_widths = [4.2, 11.8]
tbl_schema_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]

tbl_schema_data = [
    ["`tusuarios`", "Cuentas de acceso al sistema (`id`, `nombre`, `email`, `password_hash`, `rol_id`, `activo`, `ultimo_login`)."],
    ["`troles`", "Catálogo de perfiles autorizados (`id`, `nombre`: `Administrador`, `Vendedor`)."],
    ["`tclientes`", "Directorio de clientes registrados (`id`, `nombre`, `telefono`, `email`)."],
    ["`tcategorias`", "Categorías comerciales del menú (`id`, `nombre`, `descripcion`, `activo`)."],
    ["`tproductos`", "Catálogo maestro de productos (`id`, `nombre`, `categoria_id`, `precio_base`, `stock`, `stock_minimo`, `stock_maximo`, `imagen_url`, `activo`)."],
    ["`ttamanos`", "Variantes de porción/tamaño (`id`, `nombre`: `Chico`, `Mediano`, `Grande`)."],
    ["`tproductos_variantes`", "Precios específicos por variante (`id`, `producto_id`, `tamano_id`, `precio`)."],
    ["`tventas`", "Registro inmutable de transacciones (`id`, `codigo_venta`, `cliente_id`, `usuario_id`, `total`, `metodo_pago_id`, `estado_id`, `servicio`, `mesa`, `fecha_venta`)."],
    ["`tdetalleventas`", "Renglones de la orden comercial (`id`, `venta_id`, `producto_id`, `variante_id`, `cantidad`, `precio_unitario`, `subtotal`)."],
    ["`testadosventa`", "Estados de ciclo de vida del pedido (`id`, `nombre`: `Pendiente`, `En preparación`, `Entregado`, `Cancelado`)."],
    ["`tmetodospago`", "Formas de liquidación autorizadas (`id`, `nombre`: `Efectivo`, `Tarjeta`, `Transferencia`)."],
    ["`tpagos`", "Detalles monetarios del cobro (`id`, `venta_id`, `monto_recibido`, `cambio`, `referencia`)."],
    ["`tcortescaja`", "Arqueos de caja continuos (`id`, `usuario_id`, `fecha_hora_inicio`, `fecha_hora_cierre`, `total_efectivo`, `total_tarjeta`, `total_transferencia`, `total_general`, `fecha_registro`)."],
    ["`tauditoria`", "Bitácora obligatoria de trazabilidad (`id`, `usuario_id`, `accion`, `modulo`, `detalles`, `ip_origen`, `fecha`)."],
    ["`tmovimientosinventario`", "Kardex de existencias (`id`, `producto_id`, `tipo_movimiento_id`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `fecha`)."],
    ["`ttiposmovimiento`", "Catálogo de tipos de movimiento (`id`, `nombre`: `Entrada`, `Salida`, `Ajuste Manual`, `Venta`)."],
    ["`tdevoluciones`", "Registro de devoluciones y mermas (`id`, `venta_id`, `tipo_id`, `estado_id`, `motivo`)."],
    ["`testadosdevolucion`", "Estados de validación de devolución (`id`, `nombre`)."],
    ["`ttiposdevolucion`", "Tipos de devolución financiera (`id`, `nombre`)."],
    ["`tcodigosrecuperacion`", "Tokens temporales de reseteo de clave (`id`, `usuario_id`, `codigo_hash`, `expira_en`, `usado`)."],
    ["`tvalidacion_usuarios`", "Tokens de validación inicial de cuenta por correo (`id`, `usuario_id`, `codigo`, `expiracion`)."],
    ["`tschema_migrations`", "Control de versionado secuencial de base de datos (`version`, `applied_at`)."]
]

add_styled_table(tbl_schema_headers, tbl_schema_data, tbl_schema_widths, tbl_schema_align)

add_heading_2("5.2 Sistema de Migraciones Versionadas")
add_body(
    "Cualquier modificación al esquema relacional (nuevas columnas, índices, llaves) debe codificarse en "
    "un archivo SQL dentro de `database/migraciones/` siguiendo la convención de prefijo incremental "
    "`XXX_descripcion.sql` (ej. `001_ajuste_indices.sql`)."
)
add_body("Para aplicar migraciones de manera transaccional y consistente:")
add_code_block("python scripts/apply_migrations.py")
add_body(
    "El script consulta la tabla `tschema_migrations`, identifica los scripts pendientes, ejecuta cada uno "
    "dentro de una transacción segura y registra el timestamp de aplicación."
)

# ==============================================================================
# SECCIÓN 7: POOL DE CONEXIONES (BD.PY)
# ==============================================================================
print("Redactando Sección: Pool de Conexiones (bd.py)...")

add_heading_1("6. Pool de Conexiones (bd.py)")
add_body(
    "Para optimizar la concurrencia y erradicar el costo temporal de negociación de handshake TCP/TLS en "
    "cada interacción web, el módulo `bd.py` gestiona un pool centralizado basado en `PooledDB` de **DBUtils**."
)

add_heading_2("6.1 Especificación Técnica del Pool")
add_bullet("Capacidad Máxima (`maxconnections=10`):", "Límite controlado de sockets simultáneos para prevenir saturación en planes compartidos de base de datos.")
add_bullet("Precalentamiento (`mincached`):", "En desarrollo local (`APP_ENV=LOCAL`) mantiene 2 conexiones vivas en caché para latencia instantánea; en nube (`NUBE`) arranca en 0 para acelerar el inicio sin demoras de negociación SSL.")
add_bullet("Autoverificación de Salud (`ping=4`):", "Cada vez que un hilo solicita una conexión, el pool evalúa mediante un comando ping si el socket sigue operativo, reconectando automáticamente si el servidor MySQL cerró la conexión por inactividad.")
add_bullet("Tipo de Cursor (`DictCursor`):", "Configurado globalmente con `pymysql.cursors.DictCursor`, permitiendo que las consultas retornen diccionarios con nombres de columna legibles.")
add_bullet("Cifrado TLS Nube:", "Al operar en modo `NUBE`, valida la existencia del certificado CA indicado en `DB_SSL_CA` y fuerza los parámetros `ssl_verify_cert=True` y `ssl_verify_identity=True`.")

add_heading_2("6.2 Patrón de Uso en Capa de Datos (Models)")
add_body("Todas las consultas en el sistema deben seguir el patrón de liberación garantizada en bloque `try ... finally`:")

code_bd = """from bd import Obtener_Conexion

def consultar_stock_producto(producto_id):
    conn = Obtener_Conexion()
    try:
        with conn.cursor() as cursor:
            # Consulta 100% parametrizada sin concatenaciones
            sql = "SELECT id, nombre, stock, precio_base FROM tproductos WHERE id = %s AND activo = 1;"
            cursor.execute(sql, (producto_id,))
            return cursor.fetchone()
    finally:
        # Devuelve el socket al pool de forma segura (no destruye la conexión TCP)
        conn.close()"""

add_code_block(code_bd, language="python")

# ==============================================================================
# SECCIÓN 8: SEGURIDAD, AUTENTICACIÓN Y AUTORIZACIÓN
# ==============================================================================
print("Redactando Sección: Seguridad, Autenticación y Autorización...")

add_heading_1("7. Seguridad, Autenticación y Autorización")
add_body(
    "La seguridad de Coffee Hacienda POS se implementa a nivel de transporte, sesión, autorización granular "
    "y saneamiento de entradas."
)

add_heading_2("7.1 Decoradores de Control de Acceso (utils.py)")
add_bullet("Decorador `@login_required`:", "Verifica la existencia del atributo `usuario_id` en la sesión cifrada del cliente. Si el usuario no está autenticado, intercepta la petición y redirige a `/` guardando la URL original para redirección posterior.")
add_bullet("Decorador `@admin_required`:", "Verifica que el usuario posea el rol de `Administrador`. Si un usuario con perfil `Vendedor` intenta acceder a endpoints restringidos (ej. corte de caja o gestión de personal), el sistema aborta de inmediato emitiendo código HTTP **403 Forbidden**.")
add_bullet("Re-validación Activa de Sesión:", "A través de `SESSION_VALIDATION_INTERVAL_SECONDS` (def. 60 segundos), el middleware comprueba contra la tabla `tusuarios` que la cuenta continúe existiendo y mantenga el estatus `activo = 1`, revocando de inmediato sesiones de usuarios dados de baja.")

add_heading_2("7.2 Prevención de Vulnerabilidades OWASP")
add_bullet("Inyección SQL (SQLi):", "Cero tolerancia a interpolación de strings (`f\"...\"` o `%`). Todas las consultas utilizan sentencias parametrizadas nativas con tuplas de argumentos `%s` procesadas por el driver PyMySQL.")
add_bullet("Cross-Site Request Forgery (CSRF):", "Protegido integralmente mediante `Flask-WTF`. Todos los formularios POST y llamadas asíncronas `fetch()` viajan acompañadas del encabezado `X-CSRFToken` o campo oculto `csrf_token`.")
add_bullet("Mitigación de Fuerza Bruta y DoS:", "Implementado mediante `Flask-Limiter` en rutas críticas (ej. tope estricto de 5 peticiones por minuto en `/` y `/recuperar-contrasena`).")
add_bullet("Protección contra Fuga de Hashes:", "Prohibido expresamente el uso de comodines `SELECT *` o `SELECT u.*` sobre la tabla `tusuarios`, evitando que hashes de contraseñas sean expuestos en memoria.")

# ==============================================================================
# SECCIÓN 9: CATÁLOGO DE BLUEPRINTS Y RUTAS API
# ==============================================================================
print("Redactando Sección: Catálogo de Blueprints y Rutas API...")

add_heading_1("8. Catálogo de Blueprints y Rutas API")
add_body(
    "Los controladores del sistema se encuentran agrupados en **7 Blueprints** temáticos, garantizando modularidad "
    "y desacoplamiento estricto:"
)

def render_blueprint_table(title, prefix, file_name, routes_data):
    add_heading_2(f"{title} (`{file_name}` — Prefijo: `{prefix}`)")
    headers = ["Método", "Ruta del Endpoint", "Auth", "Descripción Funcional"]
    widths = [2.2, 4.8, 1.8, 7.2]
    align = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    add_styled_table(headers, routes_data, widths, align)

# 8.1 Autenticación
routes_auth = [
    ["`GET`, `POST`", "`/`", "Pública", "Pantalla de inicio de sesión y autenticación de credenciales de usuario"],
    ["`GET`", "`/salir`", "Login", "Cierre seguro de sesión activa y purga de variables de sesión"],
    ["`GET`, `POST`", "`/recuperar-contrasena`", "Pública", "Solicitud de token temporal de recuperación por correo electrónico"],
    ["`GET`, `POST`", "`/verificar-codigo`", "Pública", "Validación del código numérico de 6 dígitos enviado al usuario"],
    ["`GET`, `POST`", "`/actualizar-contrasena`", "Pública", "Asignación de nueva contraseña cifrada al usuario validado"]
]
render_blueprint_table("8.1 Blueprint de Autenticación", "/", "autenticacion_bp.py", routes_auth)

# 8.2 Ventas y POS
routes_ventas = [
    ["`GET`", "`/menu`", "Login", "Interfaz principal del Punto de Venta con categorías y carrito reactivo"],
    ["`GET`", "`/ordenes`", "Login", "Monitor visual de pedidos en cocina / barra en tiempo real"],
    ["`GET`", "`/api/ordenes`", "Login", "Consulta JSON de órdenes activas y su estado de preparación"],
    ["`GET`", "`/api/ordenes/<id>/detalles`", "Login", "Desglose pormenorizado de partidas y variantes de una orden"],
    ["`POST`", "`/api/ordenes/<id>/estado`", "Login", "Transición de estado de orden o cancelación con motivo obligatorio"],
    ["`GET`", "`/historial`", "Login", "Vista de historial de ventas con filtros de fecha y búsqueda"],
    ["`GET`", "`/api/historial-ventas`", "Login", "Listado paginado seguro (parámetro `por_pagina` acotado 1-100)"],
    ["`GET`", "`/api/historial-ventas/<id>`", "Login", "Consulta de renglones específicos de una venta consolidada"],
    ["`POST`", "`/api/ventas/crear`", "Login", "Registro transaccional de nueva venta y descuento automático de stock"],
    ["`GET`", "`/api/historial-ventas/exportar`", "Login", "Descarga de reporte de ventas filtrado en formato CSV/Excel con BOM UTF-8"]
]
render_blueprint_table("8.2 Blueprint de Ventas y POS", "/", "ventas_bp.py", routes_ventas)

# 8.3 Finanzas y Caja
routes_finanzas = [
    ["`GET`", "`/corteCaja`", "Admin", "Módulo de arqueo de caja con campo `fechaDesde` protegido"],
    ["`POST`", "`/filtrarVentas`", "Admin", "Cálculo preliminar de ventas agrupadas por método de pago"],
    ["`GET`", "`/api/corteCaja/ultimo`", "Admin", "Timestamp de cierre del último corte registrado para continuidad"],
    ["`GET`", "`/api/corteCaja/<id>`", "Admin", "Consulta de totales y desglose de un arqueo histórico"],
    ["`POST`", "`/guardarCorteCaja`", "Admin", "Registro de corte continuo garantizando ausencia de huecos temporales"],
    ["`GET`", "`/reporteFinanciero`", "Admin", "Tablero de métricas contables e histórico de cortes de caja"],
    ["`GET`", "`/api/cortes/exportar-excel`", "Admin", "Generación dinámica en memoria de archivo Excel con resumen financiero"]
]
render_blueprint_table("8.3 Blueprint de Finanzas y Caja", "/", "finanzas_bp.py", routes_finanzas)

# 8.4 Inventario
routes_inventario = [
    ["`GET`", "`/inventario`", "Admin", "Matriz de existencias, cálculo de faltantes y alertas de stock mínimo"],
    ["`POST`", "`/api/inventario/actualizar`", "Admin", "Ajuste manual de stock o límites requiriendo captura de motivo"]
]
render_blueprint_table("8.4 Blueprint de Control de Inventario", "/", "inventario_bp.py", routes_inventario)

# 8.5 Catálogo de Productos
routes_productos = [
    ["`GET`", "`/gestionProductos`", "Admin", "Administración visual del catálogo y dropzone de carga de imagen"],
    ["`GET`", "`/api/categorias`", "Admin", "Retorna listado en JSON de categorías comerciales activas"],
    ["`GET`", "`/api/tamanos`", "Admin", "Retorna catálogo de tamaños y porciones configuradas"],
    ["`POST`", "`/api/productos/guardar`", "Admin", "Alta o actualización de producto, variantes y procesamiento de imagen"],
    ["`POST`", "`/api/productos/eliminar`", "Admin", "Baja lógica (desactivación) de un producto del catálogo"],
    ["`GET`", "`/api/productos/<id>`", "Admin", "Consulta técnica de ficha de producto para edición"]
]
render_blueprint_table("8.5 Blueprint de Catálogo de Productos", "/", "productos_bp.py", routes_productos)

# 8.6 Gestión de Usuarios
routes_usuarios = [
    ["`GET`", "`/gestionUsuarios`", "Admin", "Panel de administración de colaboradores, roles y estatus"],
    ["`POST`", "`/api/usuarios/guardar`", "Admin", "Creación o edición de usuario con cifrado de contraseña"],
    ["`GET`", "`/api/usuarios/<id>`", "Admin", "Consulta de perfil de colaborador para modificación"],
    ["`POST`", "`/gestionUsuarios/eliminar/<id>`", "Admin", "Inactivación de cuenta de usuario (baja lógica)"],
    ["`POST`", "`/gestionUsuarios/activar/<id>`", "Admin", "Reactivación de acceso para un usuario previamente deshabilitado"]
]
render_blueprint_table("8.6 Blueprint de Gestión de Usuarios", "/", "usuarios_bp.py", routes_usuarios)

# 8.7 Rutas Generales y Core
routes_generales = [
    ["`GET`", "`/bienvenida`", "Login", "Pantalla de bienvenida y accesos rápidos según el rol asignado"],
    ["`GET`", "`/health`", "Pública", "Healthcheck técnico que verifica latencia y disponibilidad de MySQL"],
    ["`POST`", "`/api/guardar-pdf`", "Login", "Recepción y resguardo silencioso de comprobantes PDF en servidor"],
    ["`GET`", "`/api/pdfs/<tipo>/<nombre>`", "Login", "Descarga segura de comprobantes de tickets y cortes"]
]
render_blueprint_table("8.7 Blueprint de Servicios Generales y Core", "/", "generales_bp.py", routes_generales)

# ==============================================================================
# SECCIÓN 10: SUITE DE PRUEBAS AUTOMATIZADAS (PYTEST)
# ==============================================================================
print("Redactando Sección: Suite de Pruebas Automatizadas...")

add_heading_1("9. Suite de Pruebas Automatizadas (pytest)")
add_body(
    "Coffee Hacienda POS cuenta con una suite integral de pruebas automatizadas que garantiza la estabilidad "
    "de los flujos contables, la integridad de los endpoints y los mecanismos de autorización sin requerir "
    "conexión a una base de datos real externa."
)

add_heading_2("9.1 Comandos de Ejecución de Pruebas")
add_body("Para ejecutar la suite completa en entorno local:")
add_code_block(".venv\\Scripts\\python.exe -m pytest -p no:cacheprovider")

add_body("Para ejecutar con reporte detallado por prueba unitaria:")
add_code_block(".venv\\Scripts\\python.exe -m pytest -v -p no:cacheprovider")

add_body("Para probar un módulo de dominio aislado (ej. ventas):")
add_code_block(".venv\\Scripts\\python.exe -m pytest tests/test_ventas.py -v")

add_heading_2("9.2 Métricas de Calidad de la Suite")
add_bullet("Total de Pruebas Unitarias e Integración:", "328 casos de prueba estructurados.")
add_bullet("Pruebas Aprobadas (Passed):", "323 casos de prueba 100% superados.")
add_bullet("Pruebas Omitidas (Skipped):", "5 casos reservados estrictamente para integración continua con servidor MySQL físico activo.")
add_bullet("Fallos Detectados (Failures / Errors):", "0 fallos. Tasa de éxito del 100% en pruebas activas.")

add_heading_2("9.3 Análisis Estático de Código (Linter)")
add_body("Para mantener la limpieza de código y el cumplimiento del estándar PEP8 se utiliza **Ruff**:")
add_code_block(".venv\\Scripts\\ruff.exe check .")

# ==============================================================================
# SECCIÓN 11: GESTIÓN Y ALMACENAMIENTO DE ARCHIVOS
# ==============================================================================
print("Redactando Sección: Gestión y Almacenamiento de Archivos...")

add_heading_1("10. Gestión y Almacenamiento de Archivos")
add_body(
    "El resguardo de comprobantes, activos multimedia y reportes dinámicos se rige bajo la siguiente matriz:"
)

arch_headers = ["Tipo de Archivo", "Ubicación en Servidor", "¿En Git?", "Controlador Responsable"]
arch_widths = [3.8, 4.8, 1.8, 5.6]
arch_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]

arch_data = [
    ["**Tickets de Venta (PDF)**", "`instance/pdfs/tickets_ventas/`", "❌ No", "`/api/guardar-pdf` (Generales BP)"],
    ["**Cortes de Caja (PDF)**", "`instance/pdfs/cortes_de_caja/`", "❌ No", "jsPDF en cliente / guardado en servidor"],
    ["**Imágenes de Productos**", "`static/images/productos/`", "✅ Sí", "`/api/productos/guardar` (Productos BP)"],
    ["**Reportes Excel / CSV**", "Generación en memoria (`io.BytesIO`)", "❌ No", "`/api/historial-ventas/exportar` y `/api/cortes/exportar-excel`"]
]

add_styled_table(arch_headers, arch_data, arch_widths, arch_align)

add_alert_box(
    "note",
    "PROTECCIÓN DE LA CARPETA INSTANCE",
    "La carpeta `instance/` es aprovisionada automáticamente por la fábrica `app.py` durante el arranque "
    "mediante `os.makedirs(..., exist_ok=True)`. Permanece aislada fuera del repositorio de Git para garantizar "
    "que la información transaccional y los comprobantes de clientes no se filtren al control de versiones."
)

# ==============================================================================
# SECCIÓN 12: DESPLIEGUE EN PRODUCCIÓN Y NUBE (AIVEN)
# ==============================================================================
print("Redactando Sección: Despliegue en Producción y Nube...")

add_heading_1("11. Despliegue en Producción y Nube (Aiven)")
add_body(
    "Para desplegar Coffee Hacienda POS en un entorno de producción de alta disponibilidad con base de datos "
    "gestionada en la nube (Aiven MySQL), siga las directrices técnicas:"
)

add_heading_2("Paso 1: Configurar Parámetros de Producción en bd.env")
add_code_block(
    "APP_ENV=NUBE\n"
    "FLASK_DEBUG=False\n"
    "SECRET_KEY=clave-robusta-generada-con-openssl-rand-hex-32\n"
    "TRUST_PROXY=True\n"
    "RATELIMIT_STORAGE_URI=redis://default:password@redis-server:6379/0\n\n"
    "DB_HOST=mysql-servidor-aiven.aivencloud.com\n"
    "DB_PORT=15234\n"
    "DB_USER=avnadmin\n"
    "DB_PASSWORD=contrasena_secreta_aiven\n"
    "DB_NAME=defaultdb\n"
    "DB_SSL_CA=/etc/ssl/certs/aiven-ca.pem",
    language="ini"
)

add_heading_2("Paso 2: Servidor WSGI de Nivel de Producción")
add_body(
    "En entornos de producción está estrictamente prohibido utilizar el servidor embebido `app.run()`. "
    "Se deben emplear servidores WSGI multiproceso/multihilo:"
)
add_bullet("En Servidores Windows (Waitress):", "Ejecutar mediante el comando de producción:")
add_code_block("waitress-serve --host=0.0.0.0 --port=5000 --threads=8 app:create_app()", language="bash")

add_bullet("En Servidores Linux detrás de Nginx (Gunicorn):", "Ejecutar con workers concurrentes:")
add_code_block("gunicorn -w 4 -b 127.0.0.1:5000 \"app:create_app()\"", language="bash")

add_heading_2("Paso 3: Aplicación de Migraciones en la Nube")
add_alert_box(
    "important",
    "RESPALDO PREVIO OBLIGATORIO ANTES DE MIGRAR",
    "Antes de aplicar cualquier migración de esquema en la base de datos de producción de Aiven, debe generarse "
    "un respaldo completo de la base de datos. Una vez verificado el respaldo, aplique los cambios mediante:"
)
add_code_block("python scripts/apply_migrations.py", language="bash")

# ==============================================================================
# SECCIÓN 13: CONTROL DE VERSIONES Y FLUJO GIT
# ==============================================================================
print("Redactando Sección: Control de Versiones y Flujo Git...")

add_heading_1("12. Control de Versiones y Flujo Git")
add_body(
    "El ciclo de desarrollo colaborativo de Coffee Hacienda POS se gestiona estrictamente bajo la especificación "
    "de **Commits Semánticos** para facilitar la trazabilidad y la generación automatizada de bitácoras de cambios:"
)

git_headers = ["Prefijo Semántico", "Significado Técnico", "Ejemplo Práctico en el Repositorio"]
git_widths = [2.8, 5.0, 8.2]
git_align = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]

git_data = [
    ["`feat:`", "Nueva funcionalidad para el usuario o sistema", "`feat: exportacion de ventas en formato excel con bom utf-8`"],
    ["`fix:`", "Corrección de defecto o anomalía operativa", "`fix: validacion de huecos temporales en corte de caja continuo`"],
    ["`refactor:`", "Refactorización interna sin alterar funcionalidad", "`refactor: modularizacion de logica en blueprint de finanzas`"],
    ["`docs:`", "Modificación o ampliación de documentación técnica", "`docs: redaccion de manuales de usuario y mantenimiento`"],
    ["`test:`", "Adición o ajuste de pruebas unitarias en pytest", "`test: cobertura para validacion de limites de paginacion`"],
    ["`chore:`", "Tareas de mantenimiento, dependencias o tooling", "`chore: actualizacion de dependencias de desarrollo y ruff`"]
]

add_styled_table(git_headers, git_data, git_widths, git_align)
add_body("**Rama activa oficial de trabajo:** `feat/mejoras-operativas-pos`")

# ==============================================================================
# SECCIÓN 14: DIRECTRICES PARA AGENTES DE IA (AGENTS.MD)
# ==============================================================================
print("Redactando Sección: Directrices para Agentes de IA...")

add_heading_1("13. Directrices para Agentes de IA (AGENTS.md)")
add_body(
    "Cualquier agente de inteligencia artificial que colabore en el mantenimiento, refactorización o adición "
    "de funcionalidades en el código de Coffee Hacienda POS debe obedecer de forma ineludible las reglas "
    "consagradas en el archivo raíz `AGENTS.md`:"
)

add_bullet("1. Inmutabilidad del Historial de Ventas:", "Queda estrictamente prohibido emitir sentencias `DELETE` o `TRUNCATE` sobre las tablas `tventas` y `tdetalleventas`. Las operaciones contables son legalmente inmutables; cualquier corrección se realiza vía notas de crédito o cancelación con motivo.")
add_bullet("2. Corte de Caja Continuo (Sin Huecos Temporales):", "El campo `fechaDesde` de todo nuevo corte de caja debe calcularse y bloquearse a partir del último corte registrado (`SELECT MAX(fecha_hora_cierre) FROM tcortescaja`). No se permiten lapsos desatendidos.")
add_bullet("3. Auditoría Obligatoria y Trazabilidad:", "Toda acción que afecte el inventario (`AJUSTAR_STOCK`), anule pedidos o genere un corte de caja debe registrarse en `tauditoria` capturando usuario, timestamp, IP y motivo obligatorio.")
add_bullet("4. Consultas 100% Parametrizadas:", "Cero tolerancia a la concatenación o formateo de strings en sentencias SQL. Todas las variables deben transmitirse como parámetros tupla `%s` al driver de base de datos.")

# ==============================================================================
# SECCIÓN 15: GUÍA DE SOLUCIÓN DE PROBLEMAS (TROUBLESHOOTING)
# ==============================================================================
print("Redactando Sección: Troubleshooting...")

add_heading_1("14. Guía de Solución de Problemas (Troubleshooting)")
add_body(
    "A continuación se documentan las incidencias técnicas más comunes durante la instalación y operación, "
    "junto con su diagnóstico y solución inmediata:"
)

def add_trouble_card(err_title, cause_text, solution_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(USABLE_WIDTH_CM)
    
    set_cell_background(cell, "FEF2F2")
    set_cell_margins(cell, top=70, bottom=70, left=120, right=90)
    set_cell_borders(
        cell,
        left={'val': 'single', 'sz': '28', 'color': 'DC2626'},
        top={'val': 'single', 'sz': '4', 'color': 'FCA5A5'},
        right={'val': 'single', 'sz': '4', 'color': 'FCA5A5'},
        bottom={'val': 'single', 'sz': '4', 'color': 'FCA5A5'}
    )
    prevent_row_split(tbl.rows[0])
    
    p_t = cell.paragraphs[0]
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(2)
    r_t = p_t.add_run(f"🔴 Incidencia: {err_title}")
    r_t.bold = True
    r_t.font.name = FONT_FAMILY
    r_t.font.size = Pt(10.5)
    r_t.font.color.rgb = RGBColor(153, 27, 27)
    
    p_c = cell.add_paragraph()
    p_c.paragraph_format.space_before = Pt(1)
    p_c.paragraph_format.space_after = Pt(2)
    p_c.paragraph_format.line_spacing = 1.15
    add_formatted_runs(p_c, f"**Causa Raíz:** {cause_text}", base_size=9.5, base_color=RGBColor(69, 10, 10))
    
    p_s = cell.add_paragraph()
    p_s.paragraph_format.space_before = Pt(1)
    p_s.paragraph_format.space_after = Pt(0)
    p_s.paragraph_format.line_spacing = 1.15
    add_formatted_runs(p_s, f"**Solución Técnica:** {solution_text}", base_size=9.5, base_color=RGBColor(22, 101, 52))
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)

add_trouble_card(
    "Can't connect to MySQL server on '127.0.0.1'",
    "El servicio local de base de datos (MAMP o MySQL nativo) se encuentra detenido o configurado en un puerto diferente al 3306.",
    "Abra el panel de control de MAMP o Services de Windows, inicie el servicio MySQL y verifique que `DB_PORT=3306` en `bd.env` coincida con la escucha real."
)

add_trouble_card(
    "DB_SSL_CA no apunta a un certificado CA existente",
    "Se configuró `APP_ENV=NUBE`, pero la ruta al archivo `.pem` especificada en `DB_SSL_CA` es errónea, contiene diagonales invertidas no escapadas o el usuario del proceso carece de permisos de lectura.",
    "Proporcione una ruta absoluta normalizada con diagonales hacia adelante (ej. `C:/CoffeeHacienda/certs/aiven-ca.pem`) y valide que el archivo exista en disco."
)

add_trouble_card(
    "CSRF token missing or incorrect (HTTP 400 Bad Request)",
    "Una llamada asíncrona mediante `fetch()` o un formulario HTML enviado vía POST no incluyó el token de protección generado por Flask-WTF.",
    "Verifique que los formularios incluyan `{{ csrf_token() }}` y que las peticiones JavaScript incorporen el header `'X-CSRFToken': document.getElementById('csrf_token').value`."
)

add_trouble_card(
    "Fallo en Pytest: MySQL connection refused",
    "Una nueva prueba unitaria intentó abrir una conexión de red física con MySQL real en lugar de utilizar los mocks provistos.",
    "Utilice `monkeypatch` en el test para simular el retorno de `Obtener_Conexion()` o de los métodos de acceso a datos provistos en `tests/db_fakes.py`."
)

# Cierre y Firma Institucional
p_cierre = doc.add_paragraph()
p_cierre.paragraph_format.space_before = Pt(16)
p_cierre.paragraph_format.space_after = Pt(2)
p_cierre.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_c1 = p_cierre.add_run("Documento Oficial de Referencia Técnica y Mantenimiento — Coffee Hacienda POS\n")
r_c1.bold = True
r_c1.font.name = FONT_FAMILY
r_c1.font.size = Pt(10)
r_c1.font.color.rgb = COLOR_PRIMARY_NAVY

r_c2 = p_cierre.add_run("Coffee Hacienda — Haciendas de San Vicente, 63737 San Vicente, Nayarit, México")
r_c2.font.name = FONT_FAMILY
r_c2.font.size = Pt(9)
r_c2.font.color.rgb = COLOR_TEXT_MUTED

# ==============================================================================
# GUARDADO DE ARCHIVO WORD (.DOCX)
# ==============================================================================
print(f"Guardando documento Word en: {DOCX_PATH}")
doc.save(str(DOCX_PATH))
size_docx = DOCX_PATH.stat().st_size
print(f"Documento Word generado exitosamente. Tamaño: {size_docx:,} bytes")

# ==============================================================================
# CONVERSIÓN A PDF (.PDF) VÍA DOCX2PDF
# ==============================================================================
print("Iniciando conversión a formato PDF mediante docx2pdf...")
try:
    from docx2pdf import convert
    convert(str(DOCX_PATH), str(PDF_PATH))
    size_pdf = PDF_PATH.stat().st_size
    print(f"Conversión a PDF finalizada exitosamente en: {PDF_PATH}")
    print(f"Tamaño del archivo PDF: {size_pdf:,} bytes")
except Exception as e:
    print(f"Error durante la conversión a PDF: {e}", file=sys.stderr)
    sys.exit(1)

print("\n=== GENERACIÓN COMPLETADA CON ÉXITO ===")
