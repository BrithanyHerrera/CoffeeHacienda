# Punto de entrada de la aplicación Flask — Coffee Hacienda
import os
from flask import Flask, render_template, request, session, jsonify
from flask_mail import Mail
from dotenv import load_dotenv
from utils import login_required
from models.modelsInventario import contar_alertas_inventario
from models.modelsLimpieza import limpiar_validaciones_expiradas, limpiar_codigos_recuperacion_expirados
from extensions import limiter, csrf

load_dotenv('bd.env')

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

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
CARPETA_IMAGENES = 'static/images/productos'
app.config['UPLOAD_FOLDER'] = CARPETA_IMAGENES

# Evitar que el navegador cachee páginas dinámicas (los assets sí se cachean)
@app.after_request
def after_request(response):
    if not request.path.startswith('/static/'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── Blueprints ────────────────────────────────────────────────────────
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

# Los blueprints AJAX no usan formularios HTML, así que se exentan del CSRF
csrf.exempt(ventas_bp)
csrf.exempt(productos_bp)
csrf.exempt(usuarios_bp)
csrf.exempt(inventario_bp)
csrf.exempt(finanzas_bp)

# ── Rutas generales ──────────────────────────────────────────────────

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


# ── Guardar PDFs en el servidor ───────────────────────────────────────
import base64

CARPETA_PDFS_TICKETS = os.path.join('static', 'pdfs', 'tickets_ventas')
CARPETA_PDFS_CORTES  = os.path.join('static', 'pdfs', 'cortes_de_caja')

@app.route('/api/guardar-pdf', methods=['POST'])
@csrf.exempt
@login_required
def guardar_pdf():
    """Recibe un PDF en base64 desde el frontend y lo guarda en la carpeta correspondiente."""
    try:
        data = request.get_json()
        pdf_base64 = data.get('pdf')
        nombre_archivo = data.get('nombre', 'documento.pdf')
        tipo = data.get('tipo', 'ticket')  # 'ticket' o 'corte'

        if not pdf_base64:
            return jsonify({'success': False, 'message': 'No se recibió el PDF'}), 400

        # Sanitizar nombre del archivo
        nombre_archivo = nombre_archivo.replace('/', '_').replace('\\', '_').replace('..', '')

        carpeta = CARPETA_PDFS_TICKETS if tipo == 'ticket' else CARPETA_PDFS_CORTES
        os.makedirs(carpeta, exist_ok=True)

        ruta_completa = os.path.join(carpeta, nombre_archivo)
        pdf_bytes = base64.b64decode(pdf_base64)

        with open(ruta_completa, 'wb') as f:
            f.write(pdf_bytes)

        return jsonify({'success': True, 'ruta': ruta_completa})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al guardar PDF: {str(e)}'}), 500


if __name__ == '__main__':
    # Crear carpetas de PDFs si no existen
    os.makedirs(CARPETA_PDFS_TICKETS, exist_ok=True)
    os.makedirs(CARPETA_PDFS_CORTES, exist_ok=True)
    limpiar_validaciones_expiradas()
    limpiar_codigos_recuperacion_expirados()
    app.run(debug=True)