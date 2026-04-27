# Punto de entrada de la aplicación Flask — Coffee Hacienda
import os
from flask import Flask, render_template, request, session
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


if __name__ == '__main__':
    limpiar_validaciones_expiradas()
    limpiar_codigos_recuperacion_expirados()
    app.run(debug=True)