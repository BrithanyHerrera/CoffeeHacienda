import os
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFError

from config import config_for_environment
from extensions import limiter, csrf, mail
from models.modelsInventario import contar_alertas_inventario

def create_app(env=None):
    """Fábrica de la aplicación (Application Factory)"""
    
    # 1. Crear instancia base
    app = Flask(__name__, instance_relative_config=True)
    
    # 2. Cargar variables de entorno
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(PROJECT_ROOT, 'bd.env'))
    
    # 3. Configuración del entorno
    app_env = env or os.getenv('APP_ENV', 'LOCAL').upper()
    app.config.from_object(config_for_environment(app_env))
    es_produccion = app_env in {'NUBE', 'PRODUCTION'}
    
    # 4. Configurar Servidor de Correo
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # 5. Carpetas de almacenamiento local
    app.config['UPLOAD_FOLDER'] = os.path.join(PROJECT_ROOT, 'static', 'images', 'productos')
    app.config['PDF_TICKETS_FOLDER'] = os.path.join(app.instance_path, 'pdfs', 'tickets_ventas')
    app.config['PDF_CORTES_FOLDER'] = os.path.join(app.instance_path, 'pdfs', 'cortes_de_caja')
    
    os.makedirs(app.config['PDF_TICKETS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PDF_CORTES_FOLDER'], exist_ok=True)
    
    # 6. Proxies (Para Aiven / Producción)
    if os.getenv('TRUST_PROXY', 'False').lower() == 'true':
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
        
    # 7. Inicializar Extensiones
    limiter.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    
    # 8. Registrar Blueprints
    from blueprints.autenticacion_bp import auth_bp
    from blueprints.usuarios_bp import usuarios_bp
    from blueprints.productos_bp import productos_bp
    from blueprints.ventas_bp import ventas_bp
    from blueprints.inventario_bp import inventario_bp
    from blueprints.finanzas_bp import finanzas_bp
    from blueprints.generales_bp import core_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(finanzas_bp)
    app.register_blueprint(core_bp)
    
    # 9. Inyecciones Globales y Seguridad (Middlewares)
    @app.context_processor
    def inject_alertas():
        try:
            from flask import session
            if 'usuario' in session:
                alertas = contar_alertas_inventario()
                return {'sidebar_alertas_total': alertas['criticas'] + alertas['normales']}
        except Exception:
            pass
        return {'sidebar_alertas_total': 0}

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
            "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; font-src 'self' https://fonts.gstatic.com https://unpkg.com data:; img-src 'self' data: blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
        if es_produccion and request.is_secure:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    @app.errorhandler(CSRFError)
    def manejar_error_csrf(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'La sesión o el formulario expiró.'}), 400
        from flask import render_template
        return render_template('login.html'), 400
        
    return app

if __name__ == '__main__':
    from models.modelsLimpieza import limpiar_validaciones_expiradas, limpiar_codigos_recuperacion_expirados
    limpiar_validaciones_expiradas()
    limpiar_codigos_recuperacion_expirados()
    
    aplicacion = create_app()
    aplicacion.run(debug=aplicacion.config['DEBUG'])
