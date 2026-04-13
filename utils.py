from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta
from bd import Conexion_BD

# Extensiones de archivo permitidas para subida de imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrapped_view(*args, **kwargs):
        # Verificar si el usuario está en la sesión
        if 'usuario' not in session:
            return redirect(url_for('auth.login'))
        
        # Verificar si la sesión ha expirado por inactividad
        if 'last_activity' not in session:
            session.clear()
            return redirect(url_for('auth.login'))
        
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.now() - last_activity > timedelta(minutes=30):
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Verificar si el usuario sigue activo — solo cada 5 minutos
        # en lugar de en cada petición (ahorra ~50-100ms por clic en Aiven)
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
                cursor.execute("""
                    SELECT activo 
                    FROM tusuarios 
                    WHERE usuario = %s
                """, (session['usuario'],))
                usuario_info = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if not usuario_info or not usuario_info['activo']:
                    session.clear()
                    flash('Tu cuenta ha sido desactivada', 'danger')
                    return redirect(url_for('auth.login'))
                
                session['ultima_verificacion_activo'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error al verificar usuario activo: {e}")
        
        # Actualizar el tiempo de última actividad
        session['last_activity'] = datetime.now().isoformat()
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

def reactivar_usuario(id):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            # Actualizamos el campo activo a 1 (True) y la fecha de modificación
            sql = """
                UPDATE tusuarios 
                SET activo = 1, 
                    modificado_en = NOW() 
                WHERE Id = %s
            """
            cursor.execute(sql, (id,))
            
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error al reactivar usuario: {e}")
        return False
    finally:
        connection.close()
