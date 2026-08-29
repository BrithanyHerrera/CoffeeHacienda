# Rutas: gestión de usuarios, validación y activación
import logging
from flask import Blueprint, render_template, request, session, jsonify
from utils import login_required, admin_required, validar_fortaleza_contrasena, enviar_correo
from werkzeug.security import generate_password_hash
from extensions import limiter
from models.modelsUsuarios import (actualizar_usuario, 
                                obtener_usuario_por_id, obtener_roles, 
                                guardar_usuario_pendiente, validar_codigo_usuario,
                                reenviar_codigo_validacion,
                                obtener_usuarios_activos, obtener_usuarios_inactivos,
                                desactivar_usuario, reactivar_usuario,
                                correo_existe_en_usuarios, obtener_validacion_pendiente,
                                actualizar_correo_validacion,
                                guardar_cambio_correo_pendiente)
from models.modelsRecuperacion import generar_codigo

usuarios_bp = Blueprint('usuarios', __name__)

logger = logging.getLogger(__name__)

VALIDACION_ID_SESION = 'validacion_usuario_id'
VALIDACION_CORREO_SESION = 'validacion_usuario_correo'


def _vincular_validacion_a_sesion(validacion_id, correo):
    """Permite editar solamente la solicitud que inició esta sesión administrativa."""
    session[VALIDACION_ID_SESION] = int(validacion_id)
    session[VALIDACION_CORREO_SESION] = correo.strip().lower()


def _limpiar_validacion_de_sesion():
    session.pop(VALIDACION_ID_SESION, None)
    session.pop(VALIDACION_CORREO_SESION, None)


@usuarios_bp.route('/gestionUsuarios')
@login_required
@admin_required
def gestionUsuarios():
    usuarios_activos = obtener_usuarios_activos()
    usuarios_inactivos = obtener_usuarios_inactivos()
    roles = obtener_roles()
    return render_template('gestionUsuarios.html', 
                         usuarios_activos=usuarios_activos,
                         usuarios_inactivos=usuarios_inactivos,
                         roles=roles, 
                         rol=session.get('rol'))

@usuarios_bp.route('/api/usuarios/guardar', methods=['POST'])
@login_required
@admin_required 
def guardar_usuario():
    try:
        data = request.get_json(silent=True) or {}
        id_usuario = data.get('id')
        usuario = str(data.get('nombre') or '').strip()
        contrasena = data.get('contrasena')
        correo = str(data.get('correo') or '').strip().lower()
        rol_id = data.get('tipoPrivilegio')
        
        if not usuario or not correo or not rol_id:
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'})
        
        if id_usuario:
            # Obtener datos actuales del usuario (una sola consulta)
            usuario_actual = obtener_usuario_por_id(id_usuario)
            if not usuario_actual:
                return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            
            # El hash actual nunca se recupera: una contraseña vacía significa conservarla.
            if contrasena:
                # Validar fortaleza de la nueva contraseña
                valida, mensaje_validacion = validar_fortaleza_contrasena(contrasena)
                if not valida:
                    return jsonify({'success': False, 'message': mensaje_validacion})
            
            # Verificar si el correo cambió
            correo_cambio = usuario_actual and usuario_actual['correo'] != correo
            
            if correo_cambio:
                # Si el correo cambió, actualizar todo excepto el correo y validar el nuevo
                contrasena_para_guardar = generate_password_hash(contrasena) if contrasena else None
                resultado, mensaje = actualizar_usuario(id_usuario, usuario, contrasena_para_guardar, usuario_actual['correo'], rol_id)
                if not resultado:
                    return jsonify({'success': False, 'message': mensaje})
                
                # Crear validación para el cambio de correo
                codigo = generar_codigo()
                validacion_id = guardar_cambio_correo_pendiente(id_usuario, correo, codigo)
                
                if validacion_id:
                    _vincular_validacion_a_sesion(validacion_id, correo)
                    enviar_correo(correo, 
                        'Validación de cambio de correo - Coffee Hacienda',
                        f"Hola {usuario},\n\nPara confirmar el cambio de correo en Coffee Hacienda, ingresa este código:\n\n{codigo}\n\nExpira en 30 minutos.\n\nSaludos,\nCoffee Hacienda")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Datos actualizados. Se requiere validar el nuevo correo electrónico.',
                        'require_validation': True,
                        'email': correo
                    })
                else:
                    return jsonify({'success': True, 'message': 'Datos actualizados (no se pudo iniciar validación de correo)'})
            else:
                _limpiar_validacion_de_sesion()
                contrasena_para_guardar = generate_password_hash(contrasena) if contrasena else None
                resultado, mensaje = actualizar_usuario(id_usuario, usuario, contrasena_para_guardar, correo, rol_id)
                return jsonify({'success': resultado, 'message': mensaje})
        else:
            # Crear: requiere contraseña y pasa por validación de correo
            if not contrasena:
                return jsonify({'success': False, 'message': 'La contraseña es obligatoria para nuevos usuarios'})
            
            valida, mensaje_validacion = validar_fortaleza_contrasena(contrasena)
            if not valida:
                return jsonify({'success': False, 'message': mensaje_validacion})
                
            resultado, mensaje, datos = guardar_usuario_pendiente(usuario, generate_password_hash(contrasena), correo, rol_id)
            
            if resultado:
                _vincular_validacion_a_sesion(datos['id'], correo)
                enviar_correo(correo, 
                    'Validación de cuenta - Coffee Hacienda',
                    f"Hola {usuario},\n\nPara completar tu registro en Coffee Hacienda, ingresa este código:\n\n{datos['codigo']}\n\nExpira en 30 minutos.\n\nSaludos,\nCoffee Hacienda")
                
                return jsonify({
                    'success': True,
                    'message': 'Se ha enviado un código de validación a tu correo electrónico',
                    'require_validation': True,
                    'email': correo
                })
            else:
                return jsonify({'success': False, 'message': mensaje})
    except Exception as e:
        logger.error("Error al guardar usuario", exc_info=True)
        return jsonify({'success': False, 'message': 'No fue posible guardar el usuario'}), 500

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['GET'])
@login_required
@admin_required
def get_usuario(id):
    try:
        usuario = obtener_usuario_por_id(id)
        if usuario:
            # Defensa adicional: la API publica exclusivamente campos permitidos.
            usuario_seguro = {
                campo: usuario.get(campo)
                for campo in ('Id', 'usuario', 'correo', 'rol_id', 'rol', 'activo', 'creado_en', 'modificado_en')
            }
            return jsonify({'success': True, 'usuario': usuario_seguro})
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
    except Exception as e:
        logger.exception('Error al obtener usuario')
        return jsonify({'success': False, 'message': 'No se pudo obtener el usuario'}), 500

@usuarios_bp.route('/gestionUsuarios/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario_route(id):
    try:
        exito, mensaje = desactivar_usuario(id)
        return jsonify({'success': exito, 'message': mensaje})
    except Exception as e:
        logger.exception('Error al desactivar usuario')
        return jsonify({'success': False, 'message': 'No se pudo desactivar el usuario'}), 500

@usuarios_bp.route('/gestionUsuarios/activar/<int:id>', methods=['POST'])
@login_required
@admin_required
def activar_usuario_route(id):
    try:
        resultado = reactivar_usuario(id)
        if resultado:
            return jsonify({'success': True, 'message': 'Usuario reactivado exitosamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al reactivar usuario'})
    except Exception as e:
        logger.exception('Error al reactivar usuario')
        return jsonify({'success': False, 'message': 'No se pudo reactivar el usuario'}), 500

@usuarios_bp.route('/validar-usuario')
def validar_usuario_view():
    correo = request.args.get('email', '')
    return render_template('validar_usuario.html', correo=correo)

@usuarios_bp.route('/api/usuarios/validar', methods=['POST'])
@limiter.limit("10 per minute")
def validar_usuario_api():
    try:
        data = request.get_json(silent=True) or {}
        correo = str(data.get('correo') or '').strip().lower()
        codigo = data.get('codigo')
        
        if not correo or not codigo:
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'})
        
        resultado, mensaje = validar_codigo_usuario(correo, codigo)
        if resultado and session.get(VALIDACION_CORREO_SESION) == correo:
            _limpiar_validacion_de_sesion()
        return jsonify({'success': resultado, 'message': mensaje})
    except Exception as e:
        logger.exception('Error al validar usuario')
        return jsonify({'success': False, 'message': 'No se pudo validar el código'}), 500

@usuarios_bp.route('/api/usuarios/reenviar-codigo', methods=['POST'])
@limiter.limit("3 per minute")
def reenviar_codigo_api():
    try:
        data = request.get_json(silent=True) or {}
        correo = str(data.get('correo') or '').strip().lower()
        
        if not correo:
            return jsonify({'success': False, 'message': 'El correo electrónico es obligatorio'})
        
        resultado, mensaje, codigo = reenviar_codigo_validacion(correo)
        
        if resultado:
            enviado = enviar_correo(correo,
                'Nuevo código de validación - Coffee Hacienda',
                f"Hola,\n\nTu nuevo código de validación para Coffee Hacienda:\n\n{codigo}\n\nExpira en 30 minutos.\n\nSaludos,\nCoffee Hacienda")
            
            if enviado:
                return jsonify({'success': True, 'message': 'Se ha enviado un nuevo código de validación a tu correo electrónico'})
            else:
                return jsonify({'success': False, 'message': 'Error al enviar correo de validación'})
        else:
            return jsonify({'success': False, 'message': mensaje})
    except Exception as e:
        logger.exception('Error al reenviar código')
        return jsonify({'success': False, 'message': 'No se pudo reenviar el código'}), 500

@usuarios_bp.route('/api/usuarios/actualizar-correo', methods=['POST'])
@login_required
@admin_required
@limiter.limit("3 per minute")
def actualizar_correo_validacion_route():
    try:
        data = request.get_json(silent=True) or {}
        correo_anterior = str(data.get('correo_anterior') or '').strip().lower()
        correo_nuevo = str(data.get('correo_nuevo') or '').strip().lower()
        
        if not correo_anterior or not correo_nuevo:
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'})

        validacion_id = session.get(VALIDACION_ID_SESION)
        correo_vinculado = session.get(VALIDACION_CORREO_SESION)
        if not validacion_id or not correo_vinculado:
            return jsonify({
                'success': False,
                'message': 'La solicitud de validación no pertenece a esta sesión'
            }), 403

        validacion = obtener_validacion_pendiente(validacion_id)
        if (not validacion
                or validacion['correo'].strip().lower() != correo_vinculado
                or correo_anterior != correo_vinculado):
            _limpiar_validacion_de_sesion()
            return jsonify({
                'success': False,
                'message': 'La solicitud de validación ya no está disponible'
            }), 403

        if correo_nuevo == correo_vinculado:
            return jsonify({'success': False, 'message': 'El nuevo correo debe ser diferente al actual'})
        
        if correo_existe_en_usuarios(correo_nuevo):
            return jsonify({'success': False, 'message': 'Ya existe un usuario con ese correo electrónico'})

        nuevo_codigo = generar_codigo()
        actualizado = actualizar_correo_validacion(
            validacion_id,
            correo_vinculado,
            correo_nuevo,
            nuevo_codigo
        )
        if not actualizado:
            return jsonify({
                'success': False,
                'message': 'No fue posible actualizar esta solicitud; verifica que el correo no esté pendiente'
            }), 409

        session[VALIDACION_CORREO_SESION] = correo_nuevo
        
        enviado = enviar_correo(correo_nuevo,
            'Nuevo código de validación - Coffee Hacienda',
            f"Hola,\n\nHas actualizado tu correo para tu cuenta en Coffee Hacienda.\n\nTu nuevo código de validación:\n\n{nuevo_codigo}\n\nExpira en 30 minutos.\n\nSaludos,\nCoffee Hacienda")
        
        if enviado:
            return jsonify({'success': True, 'message': 'Correo actualizado correctamente. Se ha enviado un nuevo código de validación.'})
        else:
            return jsonify({'success': False, 'message': 'Error al enviar correo de validación'})
        
    except Exception as e:
        logger.error(f"Error al actualizar correo: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'No fue posible actualizar el correo'}), 500
