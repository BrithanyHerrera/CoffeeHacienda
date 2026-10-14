"""
Generador de la Actividad de Investigación:
Pruebas No Funcionales, Registro y Seguimiento de Defectos, y Pruebas de Regresión
Universidad de Guadalajara - Centro Universitario de la Costa
Materia: 2026 B2 Laboratorio Abierto, Pruebas
"""
import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BASE_DIR = Path(__file__).resolve().parent.parent
DOCX_PATH = BASE_DIR / 'docs' / 'academico' / 'Actividad_Investigacion_Pruebas_No_Funcionales.docx'
PDF_PATH = BASE_DIR / 'docs' / 'academico' / 'Actividad_Investigacion_Pruebas_No_Funcionales.pdf'
LOGO_PATH = BASE_DIR / 'docs' / 'academico' / 'logo_udg.png'

doc = Document()

# Configuración de márgenes estándar (2.5 cm)
for sec in doc.sections:
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)

# Paleta de colores institucionales UDG
COLOR_PRIMARY = RGBColor(15, 34, 64)       # Azul Marino UDG
COLOR_SECONDARY = RGBColor(70, 90, 120)    # Azul secundario
COLOR_TEXT = RGBColor(35, 35, 35)          # Texto estándar
HEX_PRIMARY_BG = "0F2240"
HEX_LIGHT_BG = "F7F9FC"
HEX_BORDER = "C0C8D0"

def set_cell_background(cell, fill_hex):
    """Aplica color de fondo a una celda de tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos en la celda (dxa)."""
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

def set_cell_border(cell, color="CCCCCC", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = 'Times New Roman'
    if level == 1:
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(4)
        r.font.size = Pt(13.5)
        r.font.color.rgb = COLOR_PRIMARY
    elif level == 2:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        r.font.size = Pt(12)
        r.font.color.rgb = COLOR_PRIMARY
    else:
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        r.font.size = Pt(11.5)
        r.font.color.rgb = COLOR_SECONDARY
    return p

def body(text, justify=True, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(12)
        r_pre.font.color.rgb = COLOR_TEXT

    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.color.rgb = COLOR_TEXT
    return p

def bullet_item(bold_label, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    clean_label = bold_label.strip()
    # Evitar doble viñeta si el label traía "•"
    if clean_label.startswith('•'):
        clean_label = clean_label.lstrip('•').strip()
    
    r_bold = p.add_run(clean_label)
    r_bold.bold = True
    r_bold.font.name = 'Times New Roman'
    r_bold.font.size = Pt(12)
    r_bold.font.color.rgb = COLOR_TEXT
    
    r_text = p.add_run(f' {text}')
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(12)
    r_text.font.color.rgb = COLOR_TEXT
    return p

def cell_text(cell, text, bold=False, size=10, center=False, color=None):
    cell.text = ''
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.05
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = 'Times New Roman'
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    else:
        r.font.color.rgb = COLOR_TEXT

def callout_box(title, paragraphs_data):
    """
    Crea una caja destacada elegante tipo ficha técnica.
    paragraphs_data: lista de tuplas (subtitulo_o_bullet, texto_cuerpo) o strings.
    """
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(16.0)
    set_cell_background(cell, HEX_LIGHT_BG)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    set_cell_border(cell, color=HEX_BORDER, sz="6")
    
    # Título de la caja
    p_tit = cell.paragraphs[0]
    p_tit.paragraph_format.space_before = Pt(2)
    p_tit.paragraph_format.space_after = Pt(5)
    r_icon = p_tit.add_run("■ ")
    r_icon.bold = True
    r_icon.font.name = 'Times New Roman'
    r_icon.font.size = Pt(11)
    r_icon.font.color.rgb = COLOR_PRIMARY
    
    r_t = p_tit.add_run(title)
    r_t.bold = True
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(11)
    r_t.font.color.rgb = COLOR_PRIMARY
    
    # Contenido estructurado en párrafos limpios
    for item in paragraphs_data:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        if isinstance(item, tuple):
            prefix, body_str = item
            r_pre = p.add_run(prefix)
            r_pre.bold = True
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(10.5)
            r_pre.font.color.rgb = COLOR_TEXT
            
            r_bod = p.add_run(f" {body_str}")
            r_bod.font.name = 'Times New Roman'
            r_bod.font.size = Pt(10.5)
            r_bod.font.color.rgb = COLOR_TEXT
        else:
            r_bod = p.add_run(str(item))
            r_bod.font.name = 'Times New Roman'
            r_bod.font.size = Pt(10.5)
            r_bod.font.color.rgb = COLOR_TEXT

    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(0)
    p_end.paragraph_format.space_after = Pt(4)

# =====================================================================
# PORTADA INSTITUCIONAL UDG CUCosta
# =====================================================================
doc.add_paragraph()
p_univ = doc.add_paragraph()
p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_univ.add_run('UNIVERSIDAD DE GUADALAJARA')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

p_cu = doc.add_paragraph()
p_cu.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_cu.add_run('CENTRO UNIVERSITARIO DE LA COSTA')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(13)
r.font.color.rgb = COLOR_PRIMARY

doc.add_paragraph()

if LOGO_PATH.exists():
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.add_run().add_picture(str(LOGO_PATH), width=Cm(3.2))

doc.add_paragraph()

p_tit = doc.add_paragraph()
p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_tit.paragraph_format.space_after = Pt(4)
r = p_tit.add_run('ACTIVIDAD DE INVESTIGACIÓN')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(17)
r.font.color.rgb = COLOR_PRIMARY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_sub.add_run('Pruebas No Funcionales, Registro y Seguimiento de Defectos,\ny Pruebas de Regresión')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(13.5)
r.font.color.rgb = COLOR_TEXT

doc.add_paragraph()

datos_materia = [
    ('Materia', '2026 B2 Laboratorio Abierto, Pruebas'),
    ('Profesor', 'José Francisco Reinaga Camacho'),
    ('Fecha de entrega', '14 de octubre de 2026'),
]
for label, val in datos_materia:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r1 = p.add_run(f'{label}: ')
    r1.bold = True
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11.5)
    r2 = p.add_run(val)
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11.5)

doc.add_paragraph()

p_al_tit = doc.add_paragraph()
p_al_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_al_tit.paragraph_format.space_after = Pt(2)
r = p_al_tit.add_run('Integrantes del Equipo:')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(12)

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
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)

doc.add_paragraph()
p_pie = doc.add_paragraph()
p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_pie.add_run('Puerto Vallarta, Jalisco — Octubre de 2026')
r.font.name = 'Times New Roman'
r.font.size = Pt(11)

doc.add_page_break()

# =====================================================================
# OBJETIVO Y CONTEXTO ACADÉMICO
# =====================================================================
heading('Objetivo de la Actividad', 1)
body(
    'Comprender a profundidad la importancia crítica de las pruebas no funcionales, '
    'los mecanismos formales de registro y seguimiento de defectos, y las estrategias '
    'de ejecución de pruebas de regresión dentro del proceso de aseguramiento de la '
    'calidad del software (Software Quality Assurance - SQA). A través de esta '
    'investigación se analiza cómo estos tres pilares se complementan para garantizar '
    'sistemas informáticos robustos, seguros, escalables y con alta mantenibilidad en '
    'entornos de producción reales [1], [2].'
)

# =====================================================================
# SECCIÓN 1: INVESTIGACIÓN TEÓRICA
# =====================================================================
heading('1. Investigación Teórica', 1)

# --- 1.1 PRUEBAS NO FUNCIONALES ---
heading('1.1. Pruebas No Funcionales', 2)

body(
    'Concepto y propósito: Las pruebas no funcionales corresponden a aquellas actividades '
    'de verificación y validación orientadas a evaluar los atributos de calidad, comportamiento '
    'y restricciones operativas de un sistema de software, en contraposición con las funciones '
    'o cálculos específicos que este realiza [3]. Mientras que las pruebas funcionales responden '
    'a la interrogante "¿Qué hace el sistema?", las pruebas no funcionales responden a "¿Cómo lo '
    'hace?" (es decir, con qué rapidez, bajo qué nivel de seguridad, ante cuánta carga simultánea '
    'y con qué grado de facilidad de uso) [4].'
)
body(
    'El propósito primordial de las pruebas no funcionales radica en garantizar que la aplicación '
    'sea viable, confiable y satisfactoria para los usuarios finales dentro de un entorno de '
    'producción real. Un producto de software puede ejecutar con precisión matemática cada '
    'regla de negocio, pero si tarda minutos en responder, presenta vulnerabilidades que comprometen '
    'datos confidenciales o colapsa al recibir múltiples conexiones concurrentes, dicho producto '
    'resulta completamente inútil y perjudicial para la organización [3], [5].'
)

heading('Tipos Principales de Pruebas No Funcionales', 3)
body(
    'De acuerdo con modelos internacionales de calidad como el estándar ISO/IEC 25010 '
    '(Systems and software Quality Requirements and Evaluation - SQuaRE) [3], las pruebas '
    'no funcionales se clasifican en diversas categorías esenciales:'
)

bullet_item(
    'a) Pruebas de Rendimiento (Performance Testing):',
    'Evalúan el tiempo de respuesta, la latencia, el rendimiento transaccional (throughput) '
    'y el consumo de recursos (CPU, memoria RAM, I/O en disco, ancho de banda de red) bajo condiciones '
    'definidas de trabajo. Se subdividen a su vez en: (1) Pruebas de Carga (Load Testing), para medir '
    'el comportamiento con la concurrencia normal esperada; (2) Pruebas de Estrés (Stress Testing), '
    'que someten al sistema a demandas extremas más allá de su capacidad nominal para identificar '
    'su punto de quiebre y su capacidad de recuperación; (3) Pruebas de Resistencia o Fatiga (Endurance/Soak Testing), '
    'que monitorean la estabilidad durante periodos prolongados para detectar fugas de memoria (memory leaks); '
    'y (4) Pruebas de Picos (Spike Testing), que analizan la respuesta frente a incrementos repentinos de tráfico.'
)
bullet_item(
    'b) Pruebas de Seguridad (Security Testing):',
    'Verifican que la aplicación y sus canales de comunicación protejan adecuadamente la confidencialidad, '
    'integridad, disponibilidad, autenticidad y no repudio de la información. Incluyen análisis de vulnerabilidades '
    '(basados en estándares como OWASP Top 10), pruebas de penetración (pentesting), auditorías de autenticación '
    'multifactor, control de acceso basado en roles (RBAC), mitigación de inyecciones SQL/NoSQL, blindaje '
    'contra Cross-Site Scripting (XSS), falsificación de peticiones en sitios cruzados (CSRF) y cifrado '
    'de datos tanto en reposo como en tránsito mediante TLS/HTTPS [1].'
)
bullet_item(
    'c) Pruebas de Usabilidad (Usability Testing):',
    'Miden el grado de facilidad de aprendizaje (learnability), eficiencia operativa, memorabilidad, '
    'tolerancia a fallos por parte del usuario y satisfacción subjetiva al interactuar con la interfaz humana. '
    'Se fundamentan en principios ergonómicos, heurísticas de usabilidad de Nielsen y estándares de '
    'accesibilidad web (como WCAG 2.1) para asegurar que usuarios con diversas capacidades puedan operar el sistema sin fricción.'
)
bullet_item(
    'd) Pruebas de Compatibilidad e Interoperabilidad:',
    'Aseguran que el software opere de manera consistente y uniforme a través de diferentes plataformas, '
    'sistemas operativos (Windows, Linux, macOS, Android, iOS), navegadores web (Chrome, Firefox, Safari, Edge), '
    'resoluciones de pantalla y entornos de hardware. Asimismo, validan el intercambio seguro y transparente '
    'de datos con servicios externos, APIs y bases de datos heterogéneas.'
)
bullet_item(
    'e) Pruebas de Confiabilidad y Recuperabilidad (Reliability & Disaster Recovery):',
    'Comprueban la capacidad del sistema para mantener un nivel especificado de servicio y disponibilidad '
    'ante condiciones anómalas o caídas de infraestructura. Evalúan métricas como el tiempo medio entre fallos (MTBF) '
    'y el tiempo medio de recuperación (MTTR), así como la efectividad de los respaldos automatizados y los mecanismos '
    'de conmutación por error (failover).'
)

heading('Diferencias entre Pruebas Funcionales y No Funcionales', 3)
body(
    'Aunque ambas modalidades son indispensables para certificar la calidad integral de una solución tecnológica, '
    'poseen enfoques, objetivos, orígenes de requisitos y métodos de evaluación sustancialmente distintos [4], [5]. '
    'A continuación, se presenta una tabla comparativa que sintetiza sus contrastes fundamentales:'
)

# TABLA COMPARATIVA
filas_comparativas = [
    ('Criterio de Evaluación', 'Pruebas Funcionales', 'Pruebas No Funcionales'),
    (
        'Pregunta Fundamental',
        '¿Qué hace el sistema?\n(Verifica el cumplimiento de requerimientos funcionales y reglas de negocio).',
        '¿Cómo lo hace el sistema?\n(Evalúa atributos de calidad como velocidad, seguridad y usabilidad).'
    ),
    (
        'Objetivo Primordial',
        'Validar entradas y salidas del sistema frente a las especificaciones esperadas.',
        'Asegurar la estabilidad, experiencia de usuario y resiliencia en condiciones reales.'
    ),
    (
        'Base de Especificación',
        'Casos de uso, historias de usuario, requerimientos funcionales del cliente.',
        'Atributos de calidad (ISO/IEC 25010), SLAs (Acuerdos de Nivel de Servicio) y normativas de seguridad.'
    ),
    (
        'Técnicas Comunes',
        'Partición de equivalencia, análisis de valores límite, tablas de decisión, pruebas unitarias.',
        'Pruebas de carga con usuarios virtuales, escaneo de vulnerabilidades, pruebas de estrés térmico/memoria.'
    ),
    (
        'Métricas Típicas',
        'Tasa de casos aprobados/reprobados, porcentaje de cobertura de código, defectos funcionales.',
        'Tiempo de respuesta (ms), transacciones por segundo (TPS), tasa de errores HTTP, uso de CPU y RAM.'
    ),
    (
        'Ejecución Manual',
        'Frecuente y viable tanto de forma manual como automatizada mediante scripts.',
        'Compleja de simular manualmente; requiere herramientas especializadas (ej. JMeter, k6, ZAP).'
    ),
    (
        'Momento Típico de Inicio',
        'Desde las etapas tempranas de codificación (pruebas unitarias y de módulo).',
        'Frecuentemente tras contar con módulos integrados, aunque la seguridad y rendimiento se perfilan desde la arquitectura.'
    ),
]

tbl_comp = doc.add_table(rows=len(filas_comparativas), cols=3)
tbl_comp.style = 'Table Grid'
tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, fila in enumerate(filas_comparativas):
    row = tbl_comp.rows[i]
    es_encabezado = (i == 0)
    for j, val in enumerate(fila):
        cell = row.cells[j]
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        if es_encabezado:
            set_cell_background(cell, HEX_PRIMARY_BG)
            cell_text(cell, val, bold=True, size=10, center=True, color=RGBColor(255, 255, 255))
        else:
            if i % 2 == 1:
                set_cell_background(cell, HEX_LIGHT_BG)
            cell_text(cell, val, bold=(j == 0), size=9.5, center=(j == 0))

doc.add_paragraph().paragraph_format.space_after = Pt(4)

# --- 1.2 REGISTRO Y SEGUIMIENTO DE DEFECTOS ---
heading('1.2. Registro y Seguimiento de Defectos (Defect Tracking)', 2)

body(
    '¿Qué es un defecto en software? De acuerdo con la terminología estandarizada del glosario '
    'IEEE Std 829 y el estándar ISO/IEC 24765 [1], [6], es crucial distinguir tres conceptos '
    'íntimamente relacionados pero conceptualmente distintos:'
)

bullet_item(
    'Error (Error / Mistake):',
    'Es una acción humana equivocada cometida por un analista, diseñador o programador (por ejemplo, '
    'una mala interpretación de una regla de cálculo fiscal o un error tipográfico en la lógica condicional).'
)
bullet_item(
    'Defecto o Bug (Fault / Defect):',
    'Es la manifestación estática del error en el artefacto de software (código fuente, scripts de '
    'base de datos o documentación de diseño). Constituye una imperfección interna que tiene el potencial '
    'de provocar una falla cuando se ejecuta la ruta afectada.'
)
bullet_item(
    'Fallo o Falla (Failure):',
    'Es la discrepancia dinámica visible entre el comportamiento observado del sistema durante su ejecución '
    'y el comportamiento especificado en los requerimientos. Ocurre cuando el flujo de control del programa '
    'alcanza y activa el defecto en tiempo de ejecución.'
)

body(
    'Etapas del ciclo de vida de un defecto (Bug Life Cycle): El ciclo de vida de un defecto describe '
    'la secuencia formal de estados y transiciones por los que transita una anomalía desde que es detectada '
    'por primera vez hasta que se verifica su solución y se archiva de manera concluyente [5], [6]. '
    'Los estados típicos en los flujos de ingeniería de software son:'
)

estados_defecto = [
    ('1. Nuevo (New):', 'El tester o usuario descubre una discrepancia, reúne las evidencias (capturas, logs, pasos de reproducción) y la registra en la herramienta.'),
    ('2. Asignado (Assigned):', 'El líder de QA o el gestor de proyecto revisa el reporte, valida su legitimidad, asigna severidad/prioridad y lo turna al desarrollador correspondiente.'),
    ('3. Abierto / En Progreso (Open / In Progress):', 'El desarrollador asignado investiga el defecto, reproduce el comportamiento en su entorno local y analiza la causa raíz del problema.'),
    ('4. Resuelto / Corregido (Fixed / Resolved):', 'El programador implementa la corrección en el código, añade o actualiza pruebas unitarias para prevenir regresiones y despliega el cambio al entorno de pruebas.'),
    ('5. En Espera de Retest (Pending Retest):', 'La corrección se encuentra lista y disponible en el ambiente de aseguramiento de calidad para que el equipo de pruebas verifique el parche.'),
    ('6. Re-evaluación (Retest / Testing):', 'El tester ejecuta nuevamente los pasos de reproducción sobre la versión corregida para comprobar si la anomalía desapareció.'),
    ('7. Cerrado (Closed):', 'Al comprobar que la falla ha sido completamente subsanada y no introduce efectos adversos, el estado del defecto pasa a cerrado y documentado.'),
    ('8. Reabierto (Reopened):', 'Si durante la re-evaluación el defecto persiste o la solución fue parcial, el ticket regresa al estado de abierto con nuevas anotaciones técnicas.'),
    ('Estados Alternos:', 'Rechazado (Rejected / Not a Bug, cuando el sistema funciona según lo diseñado), Duplicado (Duplicate, si ya existía un reporte previo) o Diferido (Deferred, cuando se pospone su resolución a un sprint futuro por baja prioridad).'),
]
for est, desc in estados_defecto:
    bullet_item(est, desc)

body(
    'Herramientas comunes para gestionar defectos: La gestión moderna de incidencias requiere plataformas '
    'que centralicen la trazabilidad, asignación de responsabilidades, categorización por severidad y comunicación '
    'interdisciplinaria entre desarrollo, operaciones y control de calidad [5]. Entre las más representativas destacan:'
)

bullet_item(
    'Jira (Atlassian):',
    'El estándar de facto en entornos corporativos ágiles (Scrum y Kanban). Permite la configuración detallada '
    'de flujos de trabajo personalizados, campos obligatorios para reproducción, niveles de severidad/prioridad, '
    'estimación de esfuerzos e integración directa con repositorios Git (GitHub, GitLab, Bitbucket) y pipelines de CI/CD.'
)
bullet_item(
    'Bugzilla (Mozilla):',
    'Una de las herramientas de código abierto más veteranas, robustas y confiables para el seguimiento riguroso '
    'de errores. Destaca por su potente motor de búsqueda avanzada, auditoría completa de cambios mediante '
    'correo electrónico y soporte estricto para jerarquías de dependencias entre bugs.'
)
bullet_item(
    'TestLink:',
    'Sistema web de gestión de pruebas (Test Management System) enfocado primordialmente en la administración '
    'de planes de prueba, suites y casos de prueba. Aunque su núcleo es el diseño de pruebas, se integra '
    'de forma bidireccional con rastreadores de incidencias como Jira, Bugzilla y Redmine para trazar casos de prueba con defectos.'
)
bullet_item(
    'GitHub Issues / GitLab Issues:',
    'Soluciones nativas de gestión integradas en los propios repositorios de código. Facilitan vincular un defecto '
    'directamente con ramas de trabajo, Pull Requests y commits específicos (ej. "fixes #142"), posibilitando '
    'el cierre automático del ticket una vez que el código corregido es integrado a la rama principal.'
)

# --- 1.3 PRUEBAS DE REGRESIÓN ---
heading('1.3. Pruebas de Regresión (Regression Testing)', 2)

body(
    'Objetivo y cuándo se aplican: El propósito primordial de las pruebas de regresión consiste en '
    'verificar que las modificaciones recientes introducidas en el software —tales como la adición de nuevas '
    'características, la optimización de código, parches de seguridad, refactorizaciones o la corrección de un bug— '
    'no hayan provocado efectos colaterales indeseados ni hayan corrompido funcionalidades existentes que previamente '
    'operaban de manera correcta [1], [4].'
)
body(
    'Las pruebas de regresión se deben aplicar de manera disciplinada en situaciones clave del ciclo de vida del software:'
)
bullet_item('a) Tras la corrección de un defecto:', 'Para asegurar que la modificación aplicada no quebrantó otra rutina vinculada directa o indirectamente.')
bullet_item('b) Al incorporar nuevas funcionalidades:', 'Para garantizar que los nuevos módulos o endpoints no alteren los flujos comerciales o de autenticación ya consolidados.')
bullet_item('c) Tras refactorizaciones arquitectónicas:', 'Al reestructurar clases, funciones o modelos de datos para mejorar su limpieza y eficiencia interna.')
bullet_item('d) Al actualizar dependencias o infraestructura:', 'Cuando se migra a una versión superior de lenguaje (ej. Python 3.12 a 3.13), motor de base de datos o librerías del framework.')
bullet_item('e) En cada integración y entrega continua (CI/CD):', 'Ejecutadas automáticamente ante cada solicitud de fusión (Pull Request) para autorizar despliegues a producción.')

heading('Estrategias y Herramientas Utilizadas en Pruebas de Regresión', 3)
body(
    'A medida que una base de código evoluciona, el volumen total de casos de prueba puede tornarse masivo, '
    'haciendo inviable la ejecución manual periódica. Por ello, la ingeniería de software emplea tres '
    'estrategias formales de regresión [4], [5]:'
)
bullet_item(
    '1. Regresión Total (Retest-All):',
    'Consiste en reejecutar la totalidad del catálogo de pruebas existente. Es la estrategia más exhaustiva y segura, '
    'pero demanda un alto consumo de cómputo y tiempo. Resulta factible principalmente cuando se cuenta con una '
    'suite de pruebas unitarias ligeras altamente automatizadas.'
)
bullet_item(
    '2. Selección de Pruebas de Regresión (Regression Test Selection - RTS):',
    'Analiza las diferencias en el código fuente (commits/diffs) y determina qué módulos fueron potencialmente '
    'impactados. Se seleccionan únicamente los casos de prueba cuyas rutas de ejecución tocan los componentes modificados.'
)
bullet_item(
    '3. Priorización de Casos de Prueba (Test Case Prioritization - TCP):',
    'Clasifica los casos de prueba asignándoles un orden de ejecución basado en criterios estratégicos: criticidad '
    'de negocio, probabilidad histórica de falla, cobertura de código alcanzada y tiempo de ejecución. Permite '
    'descubrir defectos en los primeros minutos de ejecución del pipeline.'
)
body(
    'Herramientas representativas: Frameworks de automatización como Pytest, JUnit, NUnit o TestNG (en capas unitarias '
    'y de integración); herramientas de navegación como Selenium WebDriver, Playwright y Cypress (para regresión de interfaces '
    'de usuario); y motores de integración continua como GitHub Actions, GitLab CI y Jenkins, encargados de '
    'orquestar y bloquear fusiones si algún test de regresión fracasa.'
)

heading('Beneficios y Desafíos de las Pruebas de Regresión', 3)
bullet_item(
    'Beneficios Principales:',
    'Brindan alta confianza y estabilidad para realizar entregas continuas; reducen drásticamente los costos de reparación '
    'al detectar regresiones en etapas tempranas; preservan la integridad histórica del sistema; y posibilitan el refactor '
    'audaz del código con una red de seguridad infalible.'
)
bullet_item(
    'Desafíos Críticos:',
    'Crecimiento exponencial del tiempo de ejecución conforme el sistema se expande; presencia de pruebas intermitentes '
    'o inestables ("Flaky Tests") que fallan por factores ajenos al código (red, latencia de base de datos); y el costo '
    'de mantenimiento continuo requerido para sincronizar los scripts de prueba cuando los flujos de negocio son actualizados.'
)

doc.add_page_break()

# =====================================================================
# SECCIÓN 2: EJEMPLO PRÁCTICO
# =====================================================================
heading('2. Ejemplos Prácticos Aplicados', 1)
body(
    'Para consolidar los conceptos abordados en la investigación teórica, a continuación se describen '
    'tres escenarios técnicos detallados que ilustran la aplicación concreta de cada tipo de prueba en '
    'proyectos reales y representativos del sector industrial y de desarrollo [2], [4].'
)

# EJEMPLO 1
callout_box(
    'CASO PRÁCTICO 1: Sistema Bancario Sometido a Pruebas de Rendimiento y Estrés',
    [
        ('Contexto del Sistema:', 'Una institución bancaria opera una plataforma digital de transferencias interbancarias (tipo SPEI) y banca móvil que atiende a cientos de miles de cuentahabientes.'),
        ('Planteamiento de la Prueba:', 'Ante la proximidad del evento comercial del "Buen Fin" y el pago de quincenas, el equipo de aseguramiento de calidad (QA) diseña una prueba de rendimiento y estrés empleando la herramienta Apache JMeter.'),
        ('Criterios de Prueba:', 'Simular un escenario de carga máxima escalonada con 15,000 usuarios virtuales concurrentes ejecutando consultas de saldo, generación de transferencias y pagos de servicios durante un periodo continuo de 2 horas.'),
        ('Hallazgo Crítico:', 'A los 8,500 usuarios concurrentes, el tiempo de respuesta promedio de las transferencias se degradó de 250 milisegundos a 18.2 segundos. Al alcanzar los 11,000 usuarios, el servidor comenzó a arrojar errores HTTP 504 (Gateway Timeout) y se observó un bloqueo mutuo (deadlock) en la tabla transaccional de cuentas bancarias por contención en el pool de conexiones de la base de datos relacional.'),
        ('Acción de Mitigación:', 'Se rediseñó la arquitectura de persistencia mediante réplicas de lectura para las consultas de saldo, se implementó una cola asíncrona de mensajes con RabbitMQ para orquestar las transferencias en lotes controlados y se optimizó el pool de conexiones de 50 a 300 conexiones reutilizables. La nueva prueba de estrés certificó la estabilidad del sistema soportando 20,000 conexiones concurrentes con tiempos de respuesta inferiores a 1.2 segundos.')
    ]
)

doc.add_page_break()

# EJEMPLO 2
callout_box(
    'CASO PRÁCTICO 2: Detección, Registro y Ciclo de Vida de un Defecto Crítico en Jira',
    [
        ('Contexto del Sistema:', 'Sistema de Punto de Venta (POS) comercial para restaurantes y cafeterías.'),
        ('Ficha Técnica de la Incidencia (Issue Key POS-184):', 'Discrepancia en el cálculo del corte de caja diario al anular ventas con tarjeta bancaria. Módulo: Finanzas (/cortes/cierre). Severidad: Alta | Prioridad: P1 - Urgente.'),
        ('Pasos para Reproducir:', '1. Iniciar sesión como cajero en el POS. 2. Registrar venta de $450.00 MXN cobrada mediante Terminal Tarjeta. 3. Acceder al módulo de ventas y proceder a la anulación justificada. 4. Ir a Generar Corte de Caja y presionar "Calcular Totales Esperados".'),
        ('Comportamiento Esperado vs Observado:', 'Esperado: El total acumulado de ventas con tarjeta debe descontar la venta anulada, reflejando $0.00. Observado: El saldo acumulado sigue sumando los $450.00 de la venta cancelada, arrojando una diferencia artificial de caja y descuadrando el arqueo final.'),
        ('Evidencia Anexa:', 'Captura de pantalla del formulario de corte de caja y volcado del log con la consulta SQL subyacente.'),
        ('Resolución y Trazabilidad:', '1. El tester registra el ticket en estado "Nuevo". El líder asigna el ticket a un desarrollador backend ("Asignado"). 2. El desarrollador reproduce la falla y descubre que la consulta SUM(total) en modelsCorteCaja.py omitía el filtro WHERE estado != "CANCELADA" ("En Progreso"). 3. El programador corrige la consulta SQL, escribe una prueba unitaria específica en tests/test_modelos_corte_caja.py para validar el filtro de anulación y envía el Pull Request ("Resuelto"). 4. El tester despliega la versión a staging, repite los 4 pasos, confirma que el arqueo calcula $0.00 exactos y que las 290 pruebas unitarias pasan limpiamente ("Verificado"). 5. El ticket se actualiza formalmente a estado "Cerrado" con referencia al commit en la rama principal.')
    ]
)

doc.add_page_break()

# EJEMPLO 3
callout_box(
    'CASO PRÁCTICO 3: Pipeline CI/CD con Pruebas de Regresión Automatizadas ante Nueva Versión',
    [
        ('Contexto del Sistema:', 'Despliegue de la versión v2.4.0 de una plataforma de comercio web y punto de venta.'),
        ('Escenario de Cambio:', 'El equipo de desarrollo incorpora una nueva funcionalidad para otorgar promociones de "Hora Feliz" (Happy Hour) con descuento automático porcentual sobre productos de cafetería.'),
        ('Riesgo de Regresión:', 'La lógica de precios es transversal; una alteración incorrecta en la función compartida de cálculo de subtotal e impuestos podría quebrar la facturación regular de pedidos a domicilio o la generación de tickets de venta.'),
        ('Ejecución del Pipeline en GitHub Actions:', 'Al enviar el Pull Request a la rama main, se dispara automáticamente el workflow de Calidad con la suite completa de 290 pruebas unitarias y de integración en el runner de GitHub.'),
        ('Alarma de Regresión Detectada:', 'El test test_calculo_total_con_iva_y_descuento_general falló inesperadamente con código de error 1. La nueva función de "Hora Feliz" sobrescribía el valor del IVA general multiplicándolo por 0 en lugar de calcularlo sobre la base neta reducida.'),
        ('Bloqueo Preventivo y Resolución:', 'El pipeline bloqueó automáticamente el merge a producción, impidiendo emitir ventas con IVA incorrecto y evitando sanciones fiscales. El desarrollador ajustó la jerarquía de aplicación de impuestos en el modelo matemático, hizo push del parche, el pipeline corrió nuevamente y las 290 pruebas aprobaron con 100% de cobertura, permitiendo un despliegue seguro.')
    ]
)

# =====================================================================
# SECCIÓN 3: ANÁLISIS REFLEXIVO
# =====================================================================
heading('3. Análisis Reflexivo', 1)

body(
    '¿Por qué las pruebas no funcionales son tan relevantes como las funcionales?',
    bold_prefix='Relevancia equivalente entre atributos funcionales y no funcionales: '
)
body(
    'En el paradigma contemporáneo de la ingeniería de software, la división entre lo funcional y lo '
    'no funcional no debe interpretarse como una jerarquía de prioridades, sino como dos caras inseparables '
    'de la misma moneda. Un software que calcula una transacción con precisión funcional absoluta carece '
    'por completo de utilidad práctica si presenta un tiempo de respuesta de sesenta segundos, si sufre caídas '
    'ante el acceso concurrente de apenas veinte cajeros, o si posee brechas de seguridad que exponen las credenciales '
    'y los datos patrimoniales de los usuarios a actores maliciosos [1], [3]. La experiencia del usuario, la continuidad '
    'operativa del negocio, el cumplimiento de regulaciones de privacidad y la reputación de la organización '
    'descansan primordialmente en atributos no funcionales como el rendimiento, la resiliencia y la seguridad [4]. '
    'Por consiguiente, concebir un producto de software como "terminado" basándose exclusivamente en que sus '
    'botones y cálculos funcionan representa un grave error técnico que suele culminar en costosos fracasos comerciales.'
)

body(
    '¿Qué papel juega el seguimiento de defectos en la mejora continua del software?',
    bold_prefix='El seguimiento de defectos como catalizador de la mejora continua: '
)
body(
    'El registro y seguimiento disciplinado de defectos trasciende por completo la simple noción de ser un "listado '
    'de pendientes por reparar". En el marco de la mejora continua (filosofías Kaizen, Agile y DevOps), el repositorio '
    'de incidencias constituye la principal fuente de inteligencia empírica del equipo de desarrollo [5], [6]. Analizar '
    'el historial de fallas permite identificar patrones sistemáticos de debilidad en la arquitectura, detectar módulos '
    'con alta densidad de defectos, evaluar la eficacia de los filtros de control de calidad y cuantificar métricas '
    'clave como el tiempo promedio de resolución y la tasa de reaparición de fallas. Más aún, cada defecto debidamente '
    'documentado impulsa el análisis de causa raíz (Root Cause Analysis - RCA), transformando el error humano en '
    'aprendizaje organizacional: se actualizan las pautas de codificación, se diseñan nuevas pruebas de regresión '
    'automatizadas para que el defecto nunca vuelva a manifestarse y se perfeccionan los procesos de diseño y estimación. '
    'De este modo, el seguimiento de defectos convierte los tropiezos del pasado en la garantía de robustez del futuro.'
)

# =====================================================================
# SECCIÓN 4: REFERENCIAS BIBLIOGRÁFICAS EN FORMATO IEEE
# =====================================================================
heading('4. Referencias Bibliográficas (Formato IEEE)', 1)

referencias_ieee = [
    (
        '[1]',
        'IEEE Standard for Software and System Test Documentation, IEEE Std 829-2008 (Revision of IEEE Std 829-1998), '
        'IEEE Computer Society, Piscataway, NJ, USA, pp. 1–128, Jul. 2008. doi: 10.1109/IEEESTD.2008.4578383.'
    ),
    (
        '[2]',
        'ISO/IEC/IEEE Systems and software engineering — Software testing — Part 1: Concepts and definitions, '
        'ISO/IEC/IEEE 29119-1:2022, International Organization for Standardization, Geneva, Switzerland, 2022.'
    ),
    (
        '[3]',
        'ISO/IEC Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) '
        '— System and software quality models, ISO/IEC 25010:2011, International Organization for Standardization, '
        'Geneva, Switzerland, 2011.'
    ),
    (
        '[4]',
        'I. Sommerville, Software Engineering, 10th ed. Boston, MA, USA: Pearson Education, 2016, pp. 225–256.'
    ),
    (
        '[5]',
        'R. S. Pressman and B. R. Maxim, Software Engineering: A Practitioner’s Approach, 9th ed. New York, NY, USA: '
        'McGraw-Hill Education, 2020, pp. 480–522.'
    ),
    (
        '[6]',
        'G. J. Myers, C. Sandler, and T. Badgett, The Art of Software Testing, 3rd ed. Hoboken, NJ, USA: '
        'John Wiley & Sons, Inc., 2012, pp. 115–148.'
    ),
]

tbl_ref = doc.add_table(rows=len(referencias_ieee), cols=2)
tbl_ref.style = 'Normal Table'
tbl_ref.alignment = WD_TABLE_ALIGNMENT.CENTER
for idx, (num, cita) in enumerate(referencias_ieee):
    row = tbl_ref.rows[idx]
    c_num = row.cells[0]
    c_txt = row.cells[1]
    
    c_num.width = Cm(1.2)
    c_txt.width = Cm(14.8)
    
    set_cell_margins(c_num, top=30, bottom=30, left=30, right=50)
    set_cell_margins(c_txt, top=30, bottom=30, left=50, right=30)
    
    cell_text(c_num, num, bold=True, size=10, center=False, color=COLOR_PRIMARY)
    cell_text(c_txt, cita, bold=False, size=10, center=False)

# Guardar documento DOCX
DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(DOCX_PATH))
print(f"Documento DOCX generado exitosamente en: {DOCX_PATH}")
