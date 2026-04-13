from flask import Flask, render_template, session
from flask_mail import Mail
from utils import login_required
from models.modelsInventario import contar_alertas_inventario

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'

# Configuración del correo electrónico
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sanvicente.coffeehacienda@gmail.com'
app.config['MAIL_PASSWORD'] = 'v f e v k x u z m r x n f b h e'
mail = Mail(app)

# Configuración para subida de imágenes
UPLOAD_FOLDER = 'static/images/productos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración para prevenir el cacheo del navegador
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ── Registrar Blueprints ──────────────────────────────────────────────
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

# ── Rutas generales (no pertenecen a un dominio específico) ───────────

@app.route('/sidebar')
@login_required
def sidebar():
    return render_template('sidebar.html')

@app.route('/bienvenida')
@login_required
def bienvenida():
    # Contar alertas directamente en MySQL (antes traía TODA la tabla)
    alertas = contar_alertas_inventario()
    
    return render_template('bienvenida.html', 
                        alertas_inventario=alertas['criticas'] + alertas['normales'],
                        alertas_criticas=alertas['criticas'],
                        alertas_normales=alertas['normales'])

@app.route('/propinas')
@login_required
def propinas():
    return render_template('propinas.html')

if __name__ == '__main__':
    app.run(debug=True)