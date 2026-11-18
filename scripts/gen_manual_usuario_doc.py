"""
Generador del Documento Word (.docx) y PDF (.pdf) para el Manual de Usuario de Coffee Hacienda POS.
Construye el documento con diseño profesional, institucional y completo.
"""

import sys
import os
import re
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx2pdf import convert

# Asegurar encoding UTF-8 en consola
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DOCX_PATH = BASE_DIR / 'docs' / 'MANUAL_USUARIO.docx'
PDF_PATH = BASE_DIR / 'docs' / 'MANUAL_USUARIO.pdf'
MD_PATH = BASE_DIR / 'docs' / 'MANUAL_USUARIO.md'
LOGO_COFFEE = BASE_DIR / 'static' / 'images' / 'logo' / 'Logo Coffee Hacienda.png'
LOGO_UDG = BASE_DIR / 'docs' / 'academico' / 'logo_udg.png'

# Colores institucionales de la cafetería
COLOR_PRIMARY_DARK = RGBColor(61, 35, 20)      # #3D2314 Café Espresso oscuro
COLOR_SECONDARY = RGBColor(111, 78, 55)        # #6F4E37 Café Tostado
COLOR_TERTIARY = RGBColor(141, 110, 99)        # #8D6E63 Café Claro / Muted
COLOR_ACCENT = RGBColor(160, 82, 45)           # #A0522D Caramelo / Siena
COLOR_BODY = RGBColor(38, 38, 38)              # #262626 Antracita suave
COLOR_CODE = RGBColor(141, 78, 37)             # #8D4E25 Café rojizo para código inline
COLOR_GRAY_MUTED = RGBColor(128, 128, 128)     # #808080 Gris para notas al pie

HEX_HEADER_BG = "4A2C11"     # Fondo encabezado de tabla
HEX_ROW_ALT = "FBF9F7"       # Fondo alterno de fila
HEX_BORDER = "D7CCC8"        # Borde sutil de tabla
HEX_CODE_BG = "F6F8FA"       # Fondo de bloque de código
HEX_CODE_BORDER = "D0D7DE"   # Borde de bloque de código

CALLOUT_CONFIG = {
    'NOTE': {
        'title': 'NOTA INFORMATIVA',
        'icon': '📌',
        'border_hex': '1565C0',
        'bg_hex': 'F0F7FF',
        'title_rgb': RGBColor(13, 71, 161),
    },
    'TIP': {
        'title': 'CONSEJO PRÁCTICO',
        'icon': '💡',
        'border_hex': '2E7D32',
        'bg_hex': 'F1F8E9',
        'title_rgb': RGBColor(27, 94, 32),
    },
    'IMPORTANT': {
        'title': 'AVISO IMPORTANTE',
        'icon': '⚠️',
        'border_hex': 'E65100',
        'bg_hex': 'FFF8E1',
        'title_rgb': RGBColor(191, 54, 12),
    },
    'WARNING': {
        'title': 'ADVERTENCIA',
        'icon': '⚡',
        'border_hex': 'D84315',
        'bg_hex': 'FBE9E7',
        'title_rgb': RGBColor(191, 54, 12),
    },
    'CAUTION': {
        'title': 'PRECAUCIÓN CRÍTICA',
        'icon': '🛑',
        'border_hex': 'C62828',
        'bg_hex': 'FFEBEE',
        'title_rgb': RGBColor(183, 28, 28),
    },
}

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=140, right=140):
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

def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_row_tbl_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def add_formatted_runs(paragraph, text, font_size=Pt(10.5), font_name="Calibri", text_color=COLOR_BODY, default_bold=False, default_italic=False):
    """
    Parsea tokens de formato markdown en el texto:
    - **negrita**
    - *cursiva*
    - `codigo`
    - [texto](enlace) -> texto
    """
    # Limpiar enlaces markdown: conservar solo el texto visible
    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Dividir texto por tokens
    token_pattern = re.compile(r'(\*\*.*?\*\*|\*[^\*]+?\*|`[^`]+?`)')
    parts = token_pattern.split(clean_text)
    
    for part in parts:
        if not part:
            continue
            
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.italic = default_italic
            run.font.name = font_name
            run.font.size = font_size
            run.font.color.rgb = text_color
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.bold = default_bold
            run.italic = True
            run.font.name = font_name
            run.font.size = font_size
            run.font.color.rgb = text_color
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(font_size.pt - 1)
            run.font.color.rgb = COLOR_CODE
        else:
            run = paragraph.add_run(part)
            run.bold = default_bold
            run.italic = default_italic
            run.font.name = font_name
            run.font.size = font_size
            run.font.color.rgb = text_color

def create_document():
    doc = Document()
    
    # Configuración de página Carta con márgenes estándar de 2.5 cm
    for sec in doc.sections:
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.right_margin = Cm(2.5)
        sec.different_first_page_header_footer = True
        
        # Limpiar encabezado y pie de la primera página
        sec.first_page_header.paragraphs[0].text = ""
        sec.first_page_footer.paragraphs[0].text = ""
        
        # Encabezado para páginas subsiguientes
        p_hdr = sec.header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hdr.paragraph_format.space_after = Pt(2)
        r_hdr = p_hdr.add_run("Coffee Hacienda POS — Manual de Usuario | v1.0")
        r_hdr.font.name = "Calibri"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = COLOR_GRAY_MUTED
        
        # Pie de página con tabla de 2 celdas para alineación izquierda y derecha
        ftr = sec.footer
        p_ftr_dummy = ftr.paragraphs[0]
        p_ftr_dummy.text = ""
        tbl_ftr = ftr.add_table(rows=1, cols=2, width=Cm(16.5))
        tbl_ftr.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Quitar bordes a la tabla del footer
        tbl_ftr._tbl.tblPr.append(parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="none"/><w:left w:val="none"/>'
            f'<w:bottom w:val="none"/><w:right w:val="none"/>'
            f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        ))
        
        # Celda izquierda del pie de página
        cell_l = tbl_ftr.cell(0, 0)
        cell_l.width = Cm(10.5)
        p_l = cell_l.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_l = p_l.add_run("☕ Cafetería La Hacienda — San Vicente, Nayarit")
        r_l.font.name = "Calibri"
        r_l.font.size = Pt(8.5)
        r_l.font.color.rgb = COLOR_GRAY_MUTED
        
        # Celda derecha del pie de página (Paginación dinámica de Word)
        cell_r = tbl_ftr.cell(0, 1)
        cell_r.width = Cm(6.0)
        p_r = cell_r.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_r1 = p_r.add_run("Página ")
        r_r1.font.name = "Calibri"
        r_r1.font.size = Pt(8.5)
        r_r1.font.color.rgb = COLOR_GRAY_MUTED
        
        run_pg = p_r.add_run()
        run_pg._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))
        run_pg.font.name = "Calibri"
        run_pg.font.size = Pt(8.5)
        run_pg.font.color.rgb = COLOR_GRAY_MUTED
        
        r_r2 = p_r.add_run(" de ")
        r_r2.font.name = "Calibri"
        r_r2.font.size = Pt(8.5)
        r_r2.font.color.rgb = COLOR_GRAY_MUTED
        
        run_num = p_r.add_run()
        run_num._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="NUMPAGES"/>'))
        run_num.font.name = "Calibri"
        run_num.font.size = Pt(8.5)
        run_num.font.color.rgb = COLOR_GRAY_MUTED
        
    return doc

def build_cover_page(doc):
    """Construye una portada sumamente profesional con logotipos e información institucional."""
    # Espaciado superior sutil
    p_top = doc.add_paragraph()
    p_top.paragraph_format.space_before = Pt(8)
    p_top.paragraph_format.space_after = Pt(2)
    
    # Logotipo UDG si existe
    if LOGO_UDG.exists():
        p_udg = doc.add_paragraph()
        p_udg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_udg.paragraph_format.space_before = Pt(0)
        p_udg.paragraph_format.space_after = Pt(6)
        p_udg.add_run().add_picture(str(LOGO_UDG), width=Cm(2.2))
        
        p_inst = doc.add_paragraph()
        p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_inst.paragraph_format.space_before = Pt(0)
        p_inst.paragraph_format.space_after = Pt(8)
        r = p_inst.add_run("Universidad de Guadalajara · Centro Universitario de la Costa")
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_TERTIARY
    
    # Logotipo de la Cafetería
    if LOGO_COFFEE.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(12)
        p_logo.add_run().add_picture(str(LOGO_COFFEE), width=Cm(6.2))
    
    # Título Principal
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(6)
    p_tit.paragraph_format.space_after = Pt(2)
    r_tit = p_tit.add_run("MANUAL DE USUARIO")
    r_tit.bold = True
    r_tit.font.name = "Calibri"
    r_tit.font.size = Pt(28)
    r_tit.font.color.rgb = COLOR_PRIMARY_DARK
    
    # Subtítulo del Sistema
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(2)
    p_sub.paragraph_format.space_after = Pt(4)
    r_sub = p_sub.add_run("Coffee Hacienda POS")
    r_sub.bold = True
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(18)
    r_sub.font.color.rgb = COLOR_SECONDARY
    
    # Descripción
    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_desc.paragraph_format.space_before = Pt(0)
    p_desc.paragraph_format.space_after = Pt(16)
    r_desc = p_desc.add_run("Sistema Integral de Punto de Venta, Control de Inventario y Operaciones")
    r_desc.italic = True
    r_desc.font.name = "Calibri"
    r_desc.font.size = Pt(11)
    r_desc.font.color.rgb = RGBColor(90, 90, 90)
    
    # Ficha Técnica / Metadatos de Portada
    meta_data = [
        ("Versión del Sistema", "1.0 Oficial (Producción)"),
        ("Fecha de Publicación", "Noviembre 2026"),
        ("Establecimiento Comercial", "Cafetería La Hacienda"),
        ("Ubicación Física", "Haciendas de San Vicente, 63737 San Vicente, Nayarit"),
        ("Arquitectura Tecnológica", "Aplicación Web (Python / Flask / MySQL)"),
        ("Perfiles de Usuario", "Administrador de Sucursal y Personal de Ventas (Caja)"),
    ]
    
    tbl_meta = doc.add_table(rows=len(meta_data), cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    
    # Borde elegante y sutil en tono café
    tbl_meta._tbl.tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:color="8D6E63"/>'
        f'<w:left w:val="single" w:sz="8" w:color="8D6E63"/>'
        f'<w:bottom w:val="single" w:sz="8" w:color="8D6E63"/>'
        f'<w:right w:val="single" w:sz="8" w:color="8D6E63"/>'
        f'<w:insideH w:val="single" w:sz="4" w:color="EFEBE9"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    ))
    
    for idx, (label, val) in enumerate(meta_data):
        row = tbl_meta.rows[idx]
        set_row_cant_split(row)
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Cm(5.2)
        c1.width = Cm(9.8)
        
        bg_col = "FDFBF9" if idx % 2 == 0 else "F7F4F0"
        for c in (c0, c1):
            set_cell_background(c, bg_col)
            set_cell_margins(c, top=80, bottom=80, left=140, right=140)
            
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = COLOR_PRIMARY_DARK
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(val)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_BODY
        
    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bot.paragraph_format.space_before = Pt(22)
    p_bot.paragraph_format.space_after = Pt(0)
    r = p_bot.add_run("Coffee Hacienda POS © 2026 — Todos los derechos reservados · Documento de Control Interno")
    r.font.name = "Calibri"
    r.font.size = Pt(8.5)
    r.font.color.rgb = COLOR_GRAY_MUTED
    
    doc.add_page_break()

def add_callout(doc, alert_type, lines):
    """Agrega una caja de alerta institucional formateada (NOTE, TIP, IMPORTANT, WARNING, CAUTION)."""
    cfg = CALLOUT_CONFIG.get(alert_type.upper(), CALLOUT_CONFIG['NOTE'])
    
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    row = table.rows[0]
    set_row_cant_split(row)
    cell = row.cells[0]
    cell.width = Cm(16.5)
    
    # Borde izquierdo grueso, los demás transparentes
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:left w:val="single" w:sz="28" w:space="0" w:color="{cfg["border_hex"]}"/>'
        f'<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    set_cell_background(cell, cfg['bg_hex'])
    set_cell_margins(cell, top=90, bottom=90, left=160, right=140)
    
    # Encabezado del Callout
    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(3)
    p_title.paragraph_format.line_spacing = 1.15
    r_icon = p_title.add_run(f"{cfg['icon']}  {cfg['title']}")
    r_icon.bold = True
    r_icon.font.name = "Calibri"
    r_icon.font.size = Pt(10)
    r_icon.font.color.rgb = cfg['title_rgb']
    
    # Párrafos de contenido dentro del Callout
    for line in lines:
        if not line.strip():
            continue
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        # Si es un bullet dentro del callout
        if line.strip().startswith(('- ', '* ')):
            bullet_text = line.strip()[2:].strip()
            p.paragraph_format.left_indent = Cm(0.4)
            r_b = p.add_run("• ")
            r_b.bold = True
            r_b.font.color.rgb = cfg['title_rgb']
            add_formatted_runs(p, bullet_text, font_size=Pt(9.5), text_color=COLOR_BODY)
        else:
            add_formatted_runs(p, line.strip(), font_size=Pt(9.5), text_color=COLOR_BODY)

    # Espacio después de la tabla
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def add_code_block(doc, lines):
    """Agrega un bloque de código o diagrama monospaciado en una caja estilizada."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    row = table.rows[0]
    set_row_cant_split(row)
    cell = row.cells[0]
    cell.width = Cm(16.5)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:color="{HEX_CODE_BORDER}"/>'
        f'<w:left w:val="single" w:sz="6" w:color="{HEX_CODE_BORDER}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:color="{HEX_CODE_BORDER}"/>'
        f'<w:right w:val="single" w:sz="6" w:color="{HEX_CODE_BORDER}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    set_cell_background(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    
    text_content = "\n".join(lines)
    r = p.add_run(text_content)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(36, 41, 47)
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def add_table_data(doc, table_lines):
    """Construye y estiliza una tabla markdown completa con cabeceras, anchos proporcionales y sombreado."""
    if len(table_lines) < 2:
        return
        
    # Extraer encabezados
    headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
    num_cols = len(headers)
    if num_cols == 0:
        return
        
    # Extraer alineaciones desde la segunda línea (separador)
    divider_cells = [c.strip() for c in table_lines[1].split('|')[1:-1]]
    alignments = []
    for div in divider_cells:
        if div.startswith(':') and div.endswith(':'):
            alignments.append(WD_ALIGN_PARAGRAPH.CENTER)
        elif div.endswith(':'):
            alignments.append(WD_ALIGN_PARAGRAPH.RIGHT)
        else:
            alignments.append(WD_ALIGN_PARAGRAPH.LEFT)
    while len(alignments) < num_cols:
        alignments.append(WD_ALIGN_PARAGRAPH.LEFT)
        
    # Extraer filas de datos
    data_rows = []
    for line in table_lines[2:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        # Rellenar si faltan celdas
        while len(cells) < num_cols:
            cells.append("")
        data_rows.append(cells[:num_cols])
        
    # Calcular anchos proporcionales de columnas basados en la longitud del texto
    total_width_cm = 16.5
    max_lens = [len(h) for h in headers]
    for row in data_rows:
        for c_idx, val in enumerate(row):
            max_lens[c_idx] = max(max_lens[c_idx], len(val))
            
    # Función de ponderación suave (raíz cúbica/cuadrada) para evitar columnas excesivamente anchas o diminutas
    weights = [max(l ** 0.65, 3.5) for l in max_lens]
    sum_weights = sum(weights)
    col_widths = [(w / sum_weights) * total_width_cm for w in weights]
    
    # Crear la tabla en el documento
    tbl = doc.add_table(rows=len(data_rows) + 1, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Bordes limpios de revista/institucionales: sin líneas verticales, líneas horizontales suaves
    tbl._tbl.tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:color="8D6E63"/>'
        f'<w:bottom w:val="single" w:sz="8" w:color="8D6E63"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:color="{HEX_BORDER}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    ))
    
    # Formatear fila de encabezados
    hdr_row = tbl.rows[0]
    set_row_cant_split(hdr_row)
    set_row_tbl_header(hdr_row)
    for c_idx, h_text in enumerate(headers):
        cell = hdr_row.cells[c_idx]
        cell.width = Cm(col_widths[c_idx])
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        p = cell.paragraphs[0]
        p.alignment = alignments[c_idx]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        add_formatted_runs(p, h_text, font_size=Pt(9.5), text_color=RGBColor(255, 255, 255), default_bold=True)
        
    # Formatear filas de datos con sombreado alterno (zebra striping)
    for r_idx, row_data in enumerate(data_rows):
        row = tbl.rows[r_idx + 1]
        set_row_cant_split(row)
        bg_col = "FFFFFF" if r_idx % 2 == 0 else HEX_ROW_ALT
        
        for c_idx, cell_value in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = Cm(col_widths[c_idx])
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            p = cell.paragraphs[0]
            p.alignment = alignments[c_idx]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.08
            add_formatted_runs(p, cell_value, font_size=Pt(9.0), text_color=COLOR_BODY)
            
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def parse_and_build_document():
    print(f"Cargando archivo fuente: {MD_PATH}")
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    lines = md_text.splitlines()
    print(f"Total de líneas leídas: {len(lines)}")
    
    doc = create_document()
    build_cover_page(doc)
    
    i = 0
    in_toc_section = False
    
    while i < len(lines):
        line = lines[i]
        
        # Línea en blanco
        if not line.strip():
            i += 1
            continue
            
        # Omitir el título de portada y ficha de versión inicial en el cuerpo
        if line.startswith('# ☕ Manual de Usuario') or line.strip().startswith('> **Versión:** 1.0'):
            i += 1
            continue
            
        # Bloques de código ```
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1 # saltar el cierre ```
            add_code_block(doc, code_lines)
            continue
            
        # Cajas de alerta Callout (> [!TYPE])
        if line.strip().startswith('> [!'):
            match = re.match(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', line.strip())
            alert_type = match.group(1) if match else 'NOTE'
            callout_lines = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith('>'):
                c_line = lines[i].strip()[1:].strip()
                callout_lines.append(c_line)
                i += 1
            add_callout(doc, alert_type, callout_lines)
            continue
            
        # Citas estándar (> ...)
        if line.strip().startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            add_callout(doc, 'NOTE', quote_lines)
            continue
            
        # Tablas markdown (| ... |)
        if line.strip().startswith('|') and '|' in line.strip()[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            add_table_data(doc, table_lines)
            continue
            
        # Separador horizontal (---)
        if re.match(r'^---+$', line.strip()):
            # Si estábamos en la tabla de contenidos y encontramos un separador, añadimos salto de página
            if in_toc_section:
                in_toc_section = False
                doc.add_page_break()
            i += 1
            continue
            
        # Encabezados markdown (#)
        if line.startswith('#'):
            h_match = re.match(r'^(#+)\s*(.*)', line)
            level = len(h_match.group(1))
            h_text = h_match.group(2).strip()
            
            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True
            
            if level == 2:
                # Nivel 1 en el documento (ej. ## 1. Inicio de Sesión)
                if 'Tabla de Contenidos' in h_text:
                    in_toc_section = True
                    
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(4)
                r = p.add_run(h_text)
                r.bold = True
                r.font.name = "Calibri"
                r.font.size = Pt(15)
                r.font.color.rgb = COLOR_PRIMARY_DARK
            elif level == 3:
                # Nivel 2 en el documento (ej. ### 1.1 Pantalla de Login)
                p.paragraph_format.space_before = Pt(11)
                p.paragraph_format.space_after = Pt(3)
                r = p.add_run(h_text)
                r.bold = True
                r.font.name = "Calibri"
                r.font.size = Pt(12.5)
                r.font.color.rgb = COLOR_SECONDARY
            else:
                # Nivel 3 o mayor (ej. #### Paso 1)
                p.paragraph_format.space_before = Pt(7)
                p.paragraph_format.space_after = Pt(2)
                r = p.add_run(h_text)
                r.bold = True
                r.font.name = "Calibri"
                r.font.size = Pt(11)
                r.font.color.rgb = COLOR_TERTIARY
                
            i += 1
            continue
            
        # Elemento de lista con viñeta (- o *)
        if re.match(r'^\s*[-*]\s+', line):
            indent_spaces = len(re.match(r'^\s*', line).group(0))
            level = 0 if indent_spaces < 2 else (1 if indent_spaces < 4 else 2)
            item_text = re.sub(r'^\s*[-*]\s+', '', line).strip()
            
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5 + level * 0.5)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            
            bullet_sym = "• " if level == 0 else ("◦ " if level == 1 else "▪ ")
            r_bullet = p.add_run(bullet_sym)
            r_bullet.bold = True
            r_bullet.font.color.rgb = COLOR_SECONDARY
            
            add_formatted_runs(p, item_text, font_size=Pt(10.5))
            i += 1
            continue
            
        # Elemento de lista numerada (1. 2. etc.)
        if re.match(r'^\s*\d+\.\s+', line):
            m = re.match(r'^\s*(\d+)\.\s+(.*)', line)
            num = m.group(1)
            item_text = m.group(2).strip()
            
            # En la tabla de contenidos, estilizamos con aspecto de índice
            p = doc.add_paragraph()
            if in_toc_section:
                p.paragraph_format.left_indent = Cm(0.6)
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                
                r_num = p.add_run(f"{num}. ")
                r_num.bold = True
                r_num.font.name = "Calibri"
                r_num.font.size = Pt(10.5)
                r_num.font.color.rgb = COLOR_SECONDARY
                
                # Quitar corchetes de enlaces en el índice
                clean_toc_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', item_text)
                r_txt = p.add_run(clean_toc_text)
                r_txt.font.name = "Calibri"
                r_txt.font.size = Pt(10.5)
                r_txt.font.color.rgb = COLOR_PRIMARY_DARK
            else:
                p.paragraph_format.left_indent = Cm(0.6)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                
                r_num = p.add_run(f"{num}. ")
                r_num.bold = True
                r_num.font.name = "Calibri"
                r_num.font.size = Pt(10.5)
                r_num.font.color.rgb = COLOR_PRIMARY_DARK
                
                add_formatted_runs(p, item_text, font_size=Pt(10.5))
                
            i += 1
            continue
            
        # Párrafo normal (acumular líneas de párrafo continuas)
        para_lines = [line.strip()]
        i += 1
        while (i < len(lines) and lines[i].strip() and 
               not lines[i].strip().startswith(('#', '```', '> [!', '>', '|', '---', '- ', '* ')) and 
               not re.match(r'^\s*\d+\.\s+', lines[i])):
            para_lines.append(lines[i].strip())
            i += 1
            
        full_para_text = " ".join(para_lines)
        
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        # Si es una nota al pie o colofón final (inicia con *)
        if full_para_text.startswith('*') and full_para_text.endswith('*') and len(full_para_text) > 2:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, full_para_text, font_size=Pt(9.0), text_color=COLOR_GRAY_MUTED, default_italic=True)
        else:
            add_formatted_runs(p, full_para_text, font_size=Pt(10.5), text_color=COLOR_BODY)

    # Asegurar que el directorio de destino exista
    DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Guardando documento Word en: {DOCX_PATH}")
    doc.save(str(DOCX_PATH))
    print("Documento Word generado exitosamente.")
    
    docx_size = DOCX_PATH.stat().st_size
    print(f"Tamaño de {DOCX_PATH.name}: {docx_size:,} bytes")
    
    # Conversión a PDF mediante docx2pdf (utiliza el motor nativo de Microsoft Word)
    print(f"Iniciando conversión a PDF: {PDF_PATH}")
    convert(str(DOCX_PATH), str(PDF_PATH))
    print("Conversión a PDF completada exitosamente.")
    
    pdf_size = PDF_PATH.stat().st_size
    print(f"Tamaño de {PDF_PATH.name}: {pdf_size:,} bytes")
    
    # Verificaciones finales
    if docx_size < 10240:
        raise ValueError(f"El archivo DOCX es demasiado pequeño ({docx_size} bytes)")
    if pdf_size < 10240:
        raise ValueError(f"El archivo PDF es demasiado pequeño ({pdf_size} bytes)")
        
    print("\n=======================================================")
    print("✓ GENERACIÓN FINALIZADA CON ÉXITO")
    print(f"  • DOCX: {DOCX_PATH} ({docx_size / 1024:.1f} KB)")
    print(f"  • PDF:  {PDF_PATH} ({pdf_size / 1024:.1f} KB)")
    print("=======================================================")

if __name__ == '__main__':
    parse_and_build_document()

