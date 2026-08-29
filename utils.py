# Helpers: login, roles, validaciones y correos
import logging
from functools import wraps
from flask import current_app, flash, jsonify, redirect, request, session, url_for
from datetime import datetime, timedelta
from bd import Conexion_BD

logger = logging.getLogger(__name__)

EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif'}


def _es_solicitud_api():
    return request.path.startswith('/api/') or request.is_json


def _sesion_invalida(mensaje='Inicia sesión para continuar'):
    session.clear()
    if _es_solicitud_api():
        return jsonify({'success': False, 'message': mensaje}), 401
    flash(mensaje, 'danger')
    return redirect(url_for('auth.login'))

def archivo_permitido(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

def login_required(f):
    @wraps(f)
    def wrapped_view(*args, **kwargs):
        if 'usuario' not in session:
            return _sesion_invalida()
        
        if ('ultima_actividad' not in session
                or 'usuario_id' not in session
                or 'sesion_version' not in session):
            session.clear()
            return _sesion_invalida()
        
        # Sesión expira tras 30 min de inactividad
        try:
            ultima_actividad = datetime.fromisoformat(session['ultima_actividad'])
        except (TypeError, ValueError):
            session.clear()
            return _sesion_invalida('La sesión no es válida')
        if datetime.now() - ultima_actividad > timedelta(minutes=30):
            return _sesion_invalida('La sesión expiró por inactividad')
        
        # Verificar que el usuario siga activo en BD (cada 5 min, no en cada request)
        ultima_verificacion = session.get('ultima_verificacion_activo')
        necesita_verificar = True
        
        if ultima_verificacion:
            try:
                tiempo_desde_verificacion = datetime.now() - datetime.fromisoformat(ultima_verificacion)
                intervalo = current_app.config.get('SESSION_VALIDATION_INTERVAL_SECONDS', 60)
                if tiempo_desde_verificacion < timedelta(seconds=intervalo):
                    necesita_verificar = False
            except (TypeError, ValueError):
                necesita_verificar = True
        
        if necesita_verificar:
            try:
                conn = Conexion_BD()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT activo, sesion_version
                            FROM tusuarios
                            WHERE Id = %s
                        """, (session['usuario_id'],))
                        usuario_info = cursor.fetchone()
                finally:
                    conn.close()
                
                if (not usuario_info
                        or not usuario_info['activo']
                        or usuario_info['sesion_version'] != session['sesion_version']):
                    session.clear()
                    return _sesion_invalida('Tu sesión ya no es válida')
                
                session['ultima_verificacion_activo'] = datetime.now().isoformat()
            except Exception as e:
                logger.error(f"Error al verificar usuario activo: {e}", exc_info=True)
                session.clear()
                return _sesion_invalida('No fue posible validar la sesión')
        
        session['ultima_actividad'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    
    return wrapped_view

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'Administrador':
            if _es_solicitud_api():
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para realizar esta acción',
                }), 403
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('bienvenida'))
        return f(*args, **kwargs)
    return decorated_function

def validar_fortaleza_contrasena(contrasena):
    """Retorna (es_valida, mensaje_error)."""
    if len(contrasena) < 8:
        return False, 'La contraseña debe tener al menos 8 caracteres'
    if not any(c.isupper() for c in contrasena):
        return False, 'La contraseña debe tener al menos una letra mayúscula'
    if not any(c.islower() for c in contrasena):
        return False, 'La contraseña debe tener al menos una letra minúscula'
    if not any(c.isdigit() for c in contrasena):
        return False, 'La contraseña debe tener al menos un número'
    return True, ''

def enviar_correo(destinatario, asunto, cuerpo):
    """Envía un correo electrónico. Retorna True si se envió, False si falló."""
    from flask import current_app
    from flask_mail import Message
    try:
        mail = current_app.extensions['mail']
        msg = Message(asunto, 
                     sender=current_app.config['MAIL_USERNAME'],
                     recipients=[destinatario])
        msg.body = cuerpo
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo a {destinatario}: {e}", exc_info=True)
        return False
