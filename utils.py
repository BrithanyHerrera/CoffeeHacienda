# Funciones auxiliares — decoradores de autenticación y validaciones
import logging
from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta
from bd import Conexion_BD

logger = logging.getLogger(__name__)

EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif'}

def archivo_permitido(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

def login_required(f):
    @wraps(f)
    def wrapped_view(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('auth.login'))
        
        if 'ultima_actividad' not in session:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Sesión expira tras 30 min de inactividad
        ultima_actividad = datetime.fromisoformat(session['ultima_actividad'])
        if datetime.now() - ultima_actividad > timedelta(minutes=30):
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Verificar que el usuario siga activo en BD (cada 5 min, no en cada request)
        ultima_verificacion = session.get('ultima_verificacion_activo')
        necesita_verificar = True
        
        if ultima_verificacion:
            tiempo_desde_verificacion = datetime.now() - datetime.fromisoformat(ultima_verificacion)
            if tiempo_desde_verificacion < timedelta(minutes=5):
                necesita_verificar = False
        
        if necesita_verificar:
            try:
                conn = Conexion_BD()
                cursor = conn.cursor()
                cursor.execute("SELECT activo FROM tusuarios WHERE usuario = %s", (session['usuario'],))
                usuario_info = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if not usuario_info or not usuario_info['activo']:
                    session.clear()
                    flash('Tu cuenta ha sido desactivada', 'danger')
                    return redirect(url_for('auth.login'))
                
                session['ultima_verificacion_activo'] = datetime.now().isoformat()
            except Exception as e:
                logger.error(f"Error al verificar usuario activo: {e}", exc_info=True)
        
        session['ultima_actividad'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    
    return wrapped_view

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'Administrador':
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
