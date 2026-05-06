# Rutas de gestión de usuarios — CRUD, validación por correo y activación/desactivación
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
                                actualizar_correo_validacion)
from models.modelsRecuperacion import generar_codigo

usuarios_bp = Blueprint('usuarios', __name__)

logger = logging.getLogger(__name__)

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
        data = request.json
        id_usuario = data.get('id')
        usuario = data.get('nombre')
        contrasena = data.get('contrasena')
        correo = data.get('correo')
        rol_id = data.get('tipoPrivilegio')
        
        if not usuario or not correo or not rol_id:
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'})
        
        if id_usuario:
            # Obtener datos actuales del usuario (una sola consulta)
            usuario_actual = obtener_usuario_por_id(id_usuario)
            
            # Si no mandó contraseña nueva, mantener la actual
            if not contrasena:
                contrasena = usuario_actual['contrasena']
            else:
                # Validar fortaleza de la nueva contraseña
                valida, mensaje_validacion = validar_fortaleza_contrasena(contrasena)
                if not valida:
                    return jsonify({'success': False, 'message': mensaje_validacion})
            
            # Verificar si el correo cambió
            correo_cambio = usuario_actual and usuario_actual['correo'] != correo
            
            if correo_cambio:
                # Si el correo cambió, actualizar todo excepto el correo y validar el nuevo
                contrasena_para_guardar = generate_password_hash(contrasena) if contrasena != usuario_actual['contrasena'] else contrasena
                resultado, mensaje = actualizar_usuario(id_usuario, usuario, contrasena_para_guardar, usuario_actual['correo'], rol_id)
                if not resultado:
                    return jsonify({'success': False, 'message': mensaje})
                
                # Crear validación para el cambio de correo
                codigo = generar_codigo()
                from models.modelsUsuarios import guardar_cambio_correo_pendiente
                exito = guardar_cambio_correo_pendiente(id_usuario, correo, codigo)
                
                if exito:
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
                contrasena_para_guardar = generate_password_hash(contrasena) if contrasena != usuario_actual['contrasena'] else contrasena
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
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}) 

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['GET'])
@login_required
def get_usuario(id):
    try:
        usuario = obtener_usuario_por_id(id)
        if usuario:
            return jsonify({'success': True, 'usuario': usuario})
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@usuarios_bp.route('/gestionUsuarios/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario_route(id):
    try:
        exito, mensaje = desactivar_usuario(id)
        return jsonify({'success': exito, 'message': mensaje})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al desactivar usuario: {str(e)}'})

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
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@usuarios_bp.route('/validar-usuario')
def validar_usuario_view():
    correo = request.args.get('email', '')
    return render_template('validar_usuario.html', correo=correo)

@usuarios_bp.route('/api/usuarios/validar', methods=['POST'])
@limiter.limit("10 per minute")
def validar_usuario_api():
    try:
        data = request.json
        correo = data.get('correo')
        codigo = data.get('codigo')
        
        if not correo or not codigo:
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'})
        
        resultado, mensaje = validar_codigo_usuario(correo, codigo)
        return jsonify({'success': resultado, 'message': mensaje})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@usuarios_bp.route('/api/usuarios/reenviar-codigo', methods=['POST'])
@limiter.limit("3 per minute")
def reenviar_codigo_api():
    try:
        data = request.json
        correo = data.get('correo')
        
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
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@usuarios_bp.route('/api/usuarios/actualizar-correo', methods=['POST'])
def actualizar_correo_validacion_route():
    try:
        data = request.json
        correo_anterior = data.get('correo_anterior')
        correo_nuevo = data.get('correo_nuevo')
        
        if not correo_anterior or not correo_nuevo:
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'})
        
        if correo_existe_en_usuarios(correo_nuevo):
            return jsonify({'success': False, 'message': 'Ya existe un usuario con ese correo electrónico'})
        
        validacion = obtener_validacion_pendiente(correo_anterior)
        if not validacion:
            return jsonify({'success': False, 'message': 'No se encontró una solicitud pendiente para este correo'})
        
        nuevo_codigo = generar_codigo()
        actualizar_correo_validacion(validacion['id'], correo_nuevo, nuevo_codigo)
        
        enviado = enviar_correo(correo_nuevo,
            'Nuevo código de validación - Coffee Hacienda',
            f"Hola,\n\nHas actualizado tu correo para tu cuenta en Coffee Hacienda.\n\nTu nuevo código de validación:\n\n{nuevo_codigo}\n\nExpira en 30 minutos.\n\nSaludos,\nCoffee Hacienda")
        
        if enviado:
            return jsonify({'success': True, 'message': 'Correo actualizado correctamente. Se ha enviado un nuevo código de validación.'})
        else:
            return jsonify({'success': False, 'message': 'Error al enviar correo de validación'})
        
    except Exception as e:
        logger.error(f"Error al actualizar correo: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
