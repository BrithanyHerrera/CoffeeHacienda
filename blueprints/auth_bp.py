# Rutas de autenticación — login, logout, recuperación de contraseña
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from datetime import datetime, timedelta
from utils import login_required, validar_fortaleza_contrasena
from models.modelsLogin import buscar_usuario_por_usuario
from models.modelsUsuarios import obtener_usuario_por_correo
from models.modelsRecuperacion import (guardar_codigo_recuperacion, verificar_codigo_recuperacion,
                                        actualizar_contrasena_por_codigo, generar_codigo)
from extensions import limiter

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        if not usuario or not contrasena:
            flash('Por favor, ingrese usuario y contraseña', 'danger')
            return render_template('login.html')
        
        usuario_info = buscar_usuario_por_usuario(usuario)
        
        if not usuario_info:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
        
        if not usuario_info['activo']:
            flash('Esta cuenta está desactivada. Contacta al administrador.', 'danger')
            return render_template('login.html')
        
        if usuario_info['contrasena'] != contrasena:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
        
        session['usuario'] = usuario
        session['usuario_id'] = usuario_info['Id']
        session['rol'] = usuario_info['rol']
        session['ultima_actividad'] = datetime.now().isoformat()
        session['ultima_verificacion_activo'] = datetime.now().isoformat()
        flash('¡Bienvenido!', 'success')
        return redirect(url_for('bienvenida'))
    
    return render_template('login.html')

@auth_bp.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
@limiter.limit("3 per minute", methods=["POST"])
def recuperar_contrasena():
    from flask import current_app
    
    if request.method == 'POST':
        correo = request.form['correo']
        usuario = obtener_usuario_por_correo(correo)
        
        if usuario:
            codigo = generar_codigo()
            expiracion = datetime.now() + timedelta(minutes=30)
            guardar_codigo_recuperacion(usuario['Id'], codigo, expiracion)
            
            session['correo_recuperacion'] = correo
            
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
                logger.error(f"Error al enviar correo: {e}", exc_info=True)
                flash('Error al enviar el correo. Por favor, intenta más tarde.', 'danger')
                return render_template('recuperarContrasena.html')
                
            return redirect(url_for('auth.verificar_codigo'))
        else:
            flash('El correo electrónico no está registrado en nuestro sistema. Por favor, verifica el correo.', 'danger')
    
    return render_template('recuperarContrasena.html')

@auth_bp.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if 'correo_recuperacion' not in session:
        flash('Por favor, inicie el proceso de recuperación nuevamente', 'danger')
        return redirect(url_for('auth.recuperar_contrasena'))
        
    if request.method == 'POST':
        codigo = request.form['codigo']
        correo = session['correo_recuperacion']
        
        usuario = obtener_usuario_por_correo(correo)
        if usuario and verificar_codigo_recuperacion(usuario['Id'], codigo):
            return redirect(url_for('auth.actualizar_contrasena'))
        else:
            flash('Código inválido o expirado', 'danger')
    
    return render_template('verificarCodigo.html')

@auth_bp.route('/actualizar-contrasena', methods=['GET', 'POST'])
def actualizar_contrasena():
    if 'correo_recuperacion' not in session:
        return redirect(url_for('auth.recuperar_contrasena'))
        
    if request.method == 'POST':
        nueva_contrasena = request.form['nueva_contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']
        
        valida, mensaje_validacion = validar_fortaleza_contrasena(nueva_contrasena)
        if not valida:
            flash(mensaje_validacion, 'danger')
            return render_template('actualizarContrasena.html')
        
        usuario = obtener_usuario_por_correo(session['correo_recuperacion'])
        
        if usuario and usuario['contrasena'] == nueva_contrasena:
            flash('La nueva contraseña no puede ser igual a la anterior', 'danger')
            return render_template('actualizarContrasena.html')
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('actualizarContrasena.html')
            
        if usuario and actualizar_contrasena_por_codigo(usuario['Id'], nueva_contrasena):
            session.pop('correo_recuperacion', None)
            session['contrasena_reseteada'] = True
            return redirect(url_for('auth.login'))
        else:
            flash('Error al actualizar la contraseña', 'danger')
    
    return render_template('actualizarContrasena.html')
