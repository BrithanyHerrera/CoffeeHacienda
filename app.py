# App principal de Coffee Hacienda
import base64
import binascii
import os
import secrets
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request, send_from_directory, session, url_for
from flask_mail import Mail
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from utils import login_required
from models.modelsInventario import contar_alertas_inventario
from models.modelsLimpieza import limpiar_validaciones_expiradas, limpiar_codigos_recuperacion_expirados
from extensions import limiter, csrf

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, 'bd.env'))

from config import config_for_environment

app = Flask(__name__, instance_relative_config=True)

app_env = os.getenv('APP_ENV', 'LOCAL').upper()
es_produccion = app_env in {'NUBE', 'PRODUCTION'}
app.config.from_object(config_for_environment(app_env))
if not app.config['SECRET_KEY']:
    raise RuntimeError('SECRET_KEY es obligatorio')
if os.getenv('TRUST_PROXY', 'False').lower() == 'true':
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

limiter.init_app(app)
csrf.init_app(app)

# Correo (configuración desde bd.env)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

# Ruta donde se guardan las imágenes de productos
CARPETA_IMAGENES = os.path.join(PROJECT_ROOT, 'static', 'images', 'productos')
app.config['UPLOAD_FOLDER'] = CARPETA_IMAGENES

# Evitar que el navegador cachee páginas dinámicas (los assets sí se cachean)
@app.after_request
def after_request(response):
    if not request.path.startswith('/static/'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault(
        'Content-Security-Policy',
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
        "font-src 'self' https://fonts.gstatic.com https://unpkg.com data:; "
        "img-src 'self' data: blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    if es_produccion and request.is_secure:
        response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    return response


@app.errorhandler(CSRFError)
def manejar_error_csrf(error):
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'La sesión o el formulario expiró. Recarga la página.'}), 400
    return render_template('login.html'), 400

# Blueprints
from blueprints.auth_bp import auth_bp
from blueprints.usuarios_bp import usuarios_bp
from blueprints.productos_bp import productos_bp
from blueprints.ventas_bp import ventas_bp
from blueprints.inventario_bp import inventario_bp
from blueprints.finanzas_bp import finanzas_bp

app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(finanzas_bp)

# Rutas generales

@app.route('/sidebar')
@login_required
def sidebar():
    return render_template('sidebar.html')

@app.context_processor
def inject_alertas():
    """Inyecta el conteo de alertas de inventario al sidebar en todas las páginas."""
    try:
        if 'usuario' in session:
            alertas = contar_alertas_inventario()
            return {'sidebar_alertas_total': alertas['criticas'] + alertas['normales']}
    except Exception:
        pass
    return {'sidebar_alertas_total': 0}

@app.route('/bienvenida')
@login_required
def bienvenida():
    alertas = contar_alertas_inventario()
    return render_template('bienvenida.html', 
                        alertas_inventario=alertas['criticas'] + alertas['normales'],
                        alertas_criticas=alertas['criticas'],
                        alertas_normales=alertas['normales'])

@app.route('/confirmar-salir')
@login_required
def confirmar_salir():
    return render_template('confirmar_salir.html')


@app.route('/health')
def health():
    """Comprueba proceso y conexión básica sin exponer configuración interna."""
    from bd import Conexion_BD

    connection = None
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 AS ok')
            result = cursor.fetchone()
        if not result or result.get('ok') != 1:
            raise RuntimeError('Respuesta inesperada de la base de datos')
        return jsonify({'status': 'ok'}), 200
    except Exception:
        app.logger.exception('La comprobación de salud falló')
        return jsonify({'status': 'unavailable'}), 503
    finally:
        if connection is not None:
            connection.close()


# Guardar PDFs (tickets y cortes) fuera de /static
CARPETA_PDFS_TICKETS = os.path.join(app.instance_path, 'pdfs', 'tickets_ventas')
CARPETA_PDFS_CORTES = os.path.join(app.instance_path, 'pdfs', 'cortes_de_caja')
CARPETAS_PDF = {
    'ticket': CARPETA_PDFS_TICKETS,
    'corte': CARPETA_PDFS_CORTES,
}
app.config['PDF_TICKETS_FOLDER'] = CARPETA_PDFS_TICKETS
app.config['PDF_CORTES_FOLDER'] = CARPETA_PDFS_CORTES
MAX_PDF_BYTES = 5 * 1024 * 1024

os.makedirs(CARPETA_PDFS_TICKETS, exist_ok=True)
os.makedirs(CARPETA_PDFS_CORTES, exist_ok=True)

@app.route('/api/guardar-pdf', methods=['POST'])
@login_required
@limiter.limit('20 per minute')
def guardar_pdf():
    """Recibe un PDF en base64 desde el frontend y lo guarda en la carpeta correspondiente."""
    try:
        data = request.get_json(silent=True) or {}
        pdf_base64 = data.get('pdf')
        nombre_archivo = data.get('nombre', 'documento.pdf')
        tipo = data.get('tipo', 'ticket')  # 'ticket' o 'corte'

        if not isinstance(pdf_base64, str) or not pdf_base64:
            return jsonify({'success': False, 'message': 'No se recibió el PDF'}), 400

        if tipo not in CARPETAS_PDF:
            return jsonify({'success': False, 'message': 'Tipo de documento no válido'}), 400

        nombre_archivo = secure_filename(str(nombre_archivo)) or 'documento.pdf'
        base_nombre, extension = os.path.splitext(nombre_archivo)
        if extension.lower() != '.pdf':
            return jsonify({'success': False, 'message': 'Solo se permiten archivos PDF'}), 400

        try:
            pdf_bytes = base64.b64decode(pdf_base64, validate=True)
        except (binascii.Error, ValueError):
            return jsonify({'success': False, 'message': 'El contenido PDF no es válido'}), 400

        if len(pdf_bytes) > MAX_PDF_BYTES:
            return jsonify({'success': False, 'message': 'El PDF excede el tamaño permitido'}), 413

        if not pdf_bytes.startswith(b'%PDF-'):
            return jsonify({'success': False, 'message': 'El archivo no tiene una firma PDF válida'}), 400

        carpeta = CARPETAS_PDF[tipo]
        marca_tiempo = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        nombre_unico = f'{base_nombre[:80]}_{marca_tiempo}_{secrets.token_hex(4)}.pdf'

        ruta_completa = os.path.join(carpeta, nombre_unico)

        with open(ruta_completa, 'xb') as f:
            f.write(pdf_bytes)

        return jsonify({
            'success': True,
            'nombre': nombre_unico,
            'url': url_for('descargar_pdf', tipo=tipo, nombre=nombre_unico),
        })
    except Exception:
        app.logger.exception('Error al guardar PDF')
        return jsonify({'success': False, 'message': 'No se pudo guardar el PDF'}), 500


@app.route('/api/pdfs/<tipo>/<path:nombre>', methods=['GET'])
@login_required
def descargar_pdf(tipo, nombre):
    carpeta = CARPETAS_PDF.get(tipo)
    nombre_seguro = secure_filename(nombre)
    if not carpeta or not nombre_seguro or nombre_seguro != nombre or not nombre.endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Documento no válido'}), 404
    return send_from_directory(carpeta, nombre_seguro, mimetype='application/pdf', max_age=0)


if __name__ == '__main__':
    limpiar_validaciones_expiradas()
    limpiar_codigos_recuperacion_expirados()
    app.run(debug=app.config['DEBUG'])
