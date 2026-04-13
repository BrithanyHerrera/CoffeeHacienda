from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from datetime import datetime, timedelta
from bd import Conexion_BD
from utils import login_required
from models.modelsLogin import verificar_usuario
from models.modelsUsuarios import obtener_usuario_por_correo
from models.modelsRecuperacion import (guardar_codigo_recuperacion, verificar_codigo_recuperacion,
                                        actualizar_contrasena_por_codigo, generar_codigo_recuperacion)
from models.modelsLimpieza import limpiar_validaciones_expiradas, limpiar_codigos_recuperacion_expirados

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        if not usuario or not contrasena:
            flash('Por favor, ingrese usuario y contraseña', 'danger')
            return render_template('login.html')
        
        # Una sola consulta que verifica usuario, contraseña, activo y rol
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.Id, u.activo, u.contrasena, r.rol 
            FROM tusuarios u
            JOIN troles r ON u.rol_id = r.Id
            WHERE u.usuario = %s
        """, (usuario,))
        usuario_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not usuario_info:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
        
        if not usuario_info['activo']:
            flash('Esta cuenta está desactivada. Contacta al administrador.', 'danger')
            return render_template('login.html')
        
        if usuario_info['contrasena'] != contrasena:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
        
        # Login exitoso — guardar en sesión
        session['usuario'] = usuario
        session['rol'] = usuario_info['rol']
        session['last_activity'] = datetime.now().isoformat()
        session['ultima_verificacion_activo'] = datetime.now().isoformat()
        flash('¡Bienvenido!', 'success')
        return redirect(url_for('bienvenida'))
    
    return render_template('login.html')

@auth_bp.route('/salir')
def salir():
    session.pop('usuario', None)  # Eliminar al usuario de la sesión
    return redirect(url_for('auth.login'))

@auth_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    from flask import current_app
    
    if request.method == 'POST':
        correo = request.form['correo']
        usuario = obtener_usuario_por_correo(correo)
        
        if usuario:
            codigo = generar_codigo_recuperacion()
            expiracion = datetime.now() + timedelta(minutes=30)
            guardar_codigo_recuperacion(usuario['Id'], codigo, expiracion)
            
            # Store email in session
            session['reset_email'] = correo
            
            try:
                mail = current_app.extensions['mail']
                msg = Message('Recuperación de Contraseña - Coffee Hacienda',
                            sender=current_app.config['MAIL_USERNAME'],
                            recipients=[correo])
                msg.body = f'''Para recuperar tu contraseña, utiliza el siguiente código:
                
{codigo}

Este código expirará en 30 minutos.

Si no solicitaste recuperar tu contraseña, ignora este mensaje.

Saludos,
Coffee Hacienda'''
                
                mail.send(msg)
                flash('Se ha enviado un código de verificación a tu correo', 'success')
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                flash('Error al enviar el correo. Por favor, intenta más tarde.', 'danger')
                return render_template('recuperarContrasena.html')
                
            return redirect(url_for('auth.verificar_codigo'))
        else:
            flash('El correo electrónico no está registrado en nuestro sistema. Por favor, verifica el correo.', 'danger')
    
    return render_template('recuperarContrasena.html')

@auth_bp.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    # Check if email is in session
    if 'reset_email' not in session:
        flash('Por favor, inicie el proceso de recuperación nuevamente', 'danger')
        return redirect(url_for('auth.recuperar_contrasena'))
        
    if request.method == 'POST':
        codigo = request.form['codigo']
        correo = session['reset_email']
        
        usuario = obtener_usuario_por_correo(correo)
        if usuario and verificar_codigo_recuperacion(usuario['Id'], codigo):
            return redirect(url_for('auth.actualizar_contrasena'))
        else:
            flash('Código inválido o expirado', 'danger')
    
    return render_template('verificarCodigo.html')

@auth_bp.route('/actualizar-contrasena', methods=['GET', 'POST'])
def actualizar_contrasena():
    if 'reset_email' not in session:
        return redirect(url_for('auth.recuperar_contrasena'))
        
    if request.method == 'POST':
        nueva_contrasena = request.form['nueva_contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']
        
        usuario = obtener_usuario_por_correo(session['reset_email'])
        
        if usuario and usuario['contrasena'] == nueva_contrasena:
            flash('La nueva contraseña no puede ser igual a la anterior', 'danger')
            return render_template('actualizarContrasena.html')
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('actualizarContrasena.html')
            
        if usuario and actualizar_contrasena_por_codigo(usuario['Id'], nueva_contrasena):
            session.pop('reset_email', None)
            # Establecer la bandera para mostrar mensaje en login
            session['password_reset'] = True
            # No mostrar flash aquí, se mostrará en la página de login
            return redirect(url_for('auth.login'))
        else:
            flash('Error al actualizar la contraseña', 'danger')
    
    return render_template('actualizarContrasena.html')
