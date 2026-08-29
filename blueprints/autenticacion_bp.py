# Rutas: login, logout y recuperación de contraseña
import logging
import secrets
import string
import time
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import validar_fortaleza_contrasena, enviar_correo
from werkzeug.security import check_password_hash, generate_password_hash
from models.modelsLogin import buscar_usuario_por_usuario
from models.modelsUsuarios import obtener_usuario_por_correo
from models.modelsRecuperacion import (guardar_codigo_recuperacion, verificar_codigo_recuperacion,
                                        actualizar_contrasena_por_codigo, eliminar_codigos_recuperacion,
                                        generar_codigo)
from extensions import limiter

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

RECUPERACION_TTL_SEGUNDOS = 30 * 60
PERMISO_CAMBIO_TTL_SEGUNDOS = 10 * 60
MAX_INTENTOS_CODIGO = 5
_ESTADO_RECUPERACION = 'estado_recuperacion_contrasena'


def _limpiar_estado_recuperacion():
    """Elimina tanto el estado actual como claves usadas por el flujo anterior."""
    session.pop(_ESTADO_RECUPERACION, None)
    session.pop('correo_recuperacion', None)
    session.pop('contrasena_reseteada', None)


def _obtener_estado_recuperacion():
    """Devuelve un estado de recuperación íntegro y vigente."""
    estado = session.get(_ESTADO_RECUPERACION)
    if not isinstance(estado, dict):
        _limpiar_estado_recuperacion()
        return None

    try:
        usuario_id = int(estado['usuario_id'])
        expira_en = float(estado['expira_en'])
    except (KeyError, TypeError, ValueError):
        _limpiar_estado_recuperacion()
        return None

    if usuario_id <= 0 or expira_en <= time.time():
        _limpiar_estado_recuperacion()
        return None

    correo = estado.get('correo')
    if not isinstance(correo, str) or not correo:
        _limpiar_estado_recuperacion()
        return None

    return estado


def _tiene_permiso_para_cambiar(estado):
    """Comprueba el permiso efímero emitido solo tras consumir un código válido."""
    permiso = estado.get('permiso_cambio')
    return (
        estado.get('verificado') is True
        and isinstance(permiso, str)
        and len(permiso) == 10
    )


def _generar_permiso_cambio():
    """Genera un permiso aleatorio compatible con codigo VARCHAR(10)."""
    alfabeto = string.ascii_letters + string.digits
    return secrets.choice(string.ascii_letters) + ''.join(
        secrets.choice(alfabeto) for _ in range(9)
    )

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
        
        if not check_password_hash(usuario_info['contrasena'], contrasena):
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
        
        session['usuario'] = usuario
        session['usuario_id'] = usuario_info['Id']
        session['rol'] = usuario_info['rol']
        session['sesion_version'] = usuario_info['sesion_version']
        session['ultima_actividad'] = datetime.now().isoformat()
        session['ultima_verificacion_activo'] = datetime.now().isoformat()
        flash('¡Bienvenido!', 'success')
        return redirect(url_for('core.bienvenida'))
    
    return render_template('login.html')

@auth_bp.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
@limiter.limit("3 per minute", methods=["POST"])
def recuperar_contrasena():
    # Entrar de nuevo a este paso reinicia cualquier autorización incompleta.
    _limpiar_estado_recuperacion()

    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        if not correo:
            flash('Ingrese un correo electrónico válido', 'danger')
            return render_template('recuperarContrasena.html')

        usuario = obtener_usuario_por_correo(correo)
        
        if usuario:
            codigo = generar_codigo()
            expiracion = datetime.now() + timedelta(minutes=30)
            if not guardar_codigo_recuperacion(usuario['Id'], codigo, expiracion):
                flash('No fue posible iniciar la recuperación. Intenta más tarde.', 'danger')
                return render_template('recuperarContrasena.html')
            
            enviado = enviar_correo(correo,
                'Recuperación de Contraseña - Coffee Hacienda',
                f"Para recuperar tu contraseña, utiliza el siguiente código:\n\n{codigo}\n\nEste código expirará en 30 minutos.\n\nSi no solicitaste recuperar tu contraseña, ignora este mensaje.\n\nSaludos,\nCoffee Hacienda")
            
            if enviado:
                session[_ESTADO_RECUPERACION] = {
                    'usuario_id': int(usuario['Id']),
                    'correo': correo,
                    'expira_en': int(time.time()) + RECUPERACION_TTL_SEGUNDOS,
                    'verificado': False,
                    'intentos': 0,
                }
                flash('Se ha enviado un código de verificación a tu correo', 'success')
            else:
                eliminar_codigos_recuperacion(usuario['Id'])
                _limpiar_estado_recuperacion()
                flash('Error al enviar el correo. Por favor, intenta más tarde.', 'danger')
                return render_template('recuperarContrasena.html')
                
            return redirect(url_for('auth.verificar_codigo'))
        else:
            flash('El correo electrónico no está registrado en nuestro sistema. Por favor, verifica el correo.', 'danger')
    
    return render_template('recuperarContrasena.html')

@auth_bp.route('/verificar-codigo', methods=['GET', 'POST'])
@limiter.limit("5 per 10 minutes", methods=["POST"])
def verificar_codigo():
    estado = _obtener_estado_recuperacion()
    if not estado:
        flash('Por favor, inicie el proceso de recuperación nuevamente', 'danger')
        return redirect(url_for('auth.recuperar_contrasena'))

    if _tiene_permiso_para_cambiar(estado):
        return redirect(url_for('auth.actualizar_contrasena'))
        
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        permiso_cambio = _generar_permiso_cambio()
        expiracion_permiso = datetime.now() + timedelta(
            seconds=PERMISO_CAMBIO_TTL_SEGUNDOS
        )

        if (len(codigo) == 6 and codigo.isdigit()
                and verificar_codigo_recuperacion(
                    estado['usuario_id'],
                    codigo,
                    consumir=True,
                    codigo_consumido=permiso_cambio,
                    expiracion_consumido=expiracion_permiso,
                )):
            # El código recibido se canjeó por un permiso aleatorio de un solo uso.
            estado['verificado'] = True
            estado['permiso_cambio'] = permiso_cambio
            estado['expira_en'] = int(time.time()) + PERMISO_CAMBIO_TTL_SEGUNDOS
            estado.pop('intentos', None)
            session[_ESTADO_RECUPERACION] = estado
            return redirect(url_for('auth.actualizar_contrasena'))

        intentos = int(estado.get('intentos', 0)) + 1
        if intentos >= MAX_INTENTOS_CODIGO:
            eliminar_codigos_recuperacion(estado['usuario_id'])
            _limpiar_estado_recuperacion()
            flash('Se agotaron los intentos. Solicita un código nuevo.', 'danger')
            return redirect(url_for('auth.recuperar_contrasena'))

        estado['intentos'] = intentos
        session[_ESTADO_RECUPERACION] = estado
        flash('Código inválido o expirado', 'danger')
    
    return render_template('verificarCodigo.html')

@auth_bp.route('/actualizar-contrasena', methods=['GET', 'POST'])
@limiter.limit("5 per 10 minutes", methods=["POST"])
def actualizar_contrasena():
    estado = _obtener_estado_recuperacion()
    if not estado:
        flash('La recuperación expiró. Solicita un código nuevo.', 'danger')
        return redirect(url_for('auth.recuperar_contrasena'))

    if not _tiene_permiso_para_cambiar(estado):
        flash('Primero debes verificar el código enviado a tu correo.', 'danger')
        return redirect(url_for('auth.verificar_codigo'))

    usuario = obtener_usuario_por_correo(estado['correo'])
    if not usuario or int(usuario['Id']) != int(estado['usuario_id']):
        _limpiar_estado_recuperacion()
        flash('No fue posible validar la recuperación. Inicia nuevamente.', 'danger')
        return redirect(url_for('auth.recuperar_contrasena'))
        
    if request.method == 'POST':
        nueva_contrasena = request.form.get('nueva_contrasena', '')
        confirmar_contrasena = request.form.get('confirmar_contrasena', '')
        
        valida, mensaje_validacion = validar_fortaleza_contrasena(nueva_contrasena)
        if not valida:
            flash(mensaje_validacion, 'danger')
            return render_template('actualizarContrasena.html')
        
        if check_password_hash(usuario['contrasena'], nueva_contrasena):
            flash('La nueva contraseña no puede ser igual a la anterior', 'danger')
            return render_template('actualizarContrasena.html')
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('actualizarContrasena.html')
            
        actualizada = actualizar_contrasena_por_codigo(
            usuario['Id'],
            generate_password_hash(nueva_contrasena),
            estado['permiso_cambio'],
        )
        # Toda solicitud final válida consume el estado local. La transacción en
        # BD impide reutilizar el permiso incluso con una copia de la cookie.
        _limpiar_estado_recuperacion()

        if actualizada:
            flash('Tu contraseña se actualizó correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('La autorización ya no es válida. Solicita un código nuevo.', 'danger')
            return redirect(url_for('auth.recuperar_contrasena'))
    
    return render_template('actualizarContrasena.html')
