# Rutas de gestión de usuarios — CRUD, validación por correo y activación/desactivación
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_mail import Message
from datetime import datetime
from utils import login_required, admin_required, validar_fortaleza_contrasena
from models.modelsUsuarios import (obtener_usuarios, crear_usuario, actualizar_usuario, 
                                obtener_usuario_por_id, obtener_roles, 
                                obtener_usuario_por_correo,
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
            # Editar: si no mandó contraseña nueva, mantener la actual
            if not contrasena:
                usuario_actual = obtener_usuario_por_id(id_usuario)
                contrasena = usuario_actual['contrasena']
                
            resultado, mensaje = actualizar_usuario(id_usuario, usuario, contrasena, correo, rol_id)
            return jsonify({'success': resultado, 'message': mensaje})
        else:
            # Crear: requiere contraseña y pasa por validación de correo
            if not contrasena:
                return jsonify({'success': False, 'message': 'La contraseña es obligatoria para nuevos usuarios'})
            
            valida, mensaje_validacion = validar_fortaleza_contrasena(contrasena)
            if not valida:
                return jsonify({'success': False, 'message': mensaje_validacion})
                
            resultado, mensaje, datos = guardar_usuario_pendiente(usuario, contrasena, correo, rol_id)
            
            if resultado:
                try:
                    mail = current_app.extensions['mail']
                    msg = Message('Validación de cuenta - Coffee Hacienda', 
                                sender=current_app.config['MAIL_USERNAME'],
                                recipients=[correo])
                    msg.body = f"""Hola {usuario},

Para completar tu registro en Coffee Hacienda, ingresa este código:

{datos['codigo']}

Expira en 30 minutos.

Saludos,
Coffee Hacienda"""
                    mail.send(msg)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Se ha enviado un código de validación a tu correo electrónico',
                        'require_validation': True,
                        'email': correo
                    })
                except Exception as e:
                    logger.error(f"Error al enviar correo: {e}", exc_info=True)
                    return jsonify({'success': False, 'message': f'Error al enviar correo de validación: {str(e)}'})
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
def reenviar_codigo_api():
    try:
        data = request.json
        correo = data.get('correo')
        
        if not correo:
            return jsonify({'success': False, 'message': 'El correo electrónico es obligatorio'})
        
        resultado, mensaje, codigo = reenviar_codigo_validacion(correo)
        
        if resultado:
            try:
                mail = current_app.extensions['mail']
                msg = Message('Nuevo código de validación - Coffee Hacienda', 
                            sender=current_app.config['MAIL_USERNAME'],
                            recipients=[correo])
                msg.body = f"""Hola,

Tu nuevo código de validación para Coffee Hacienda:

{codigo}

Expira en 24 horas.

Saludos,
Coffee Hacienda"""
                mail.send(msg)
                return jsonify({'success': True, 'message': 'Se ha enviado un nuevo código de validación a tu correo electrónico'})
            except Exception as e:
                logger.error(f"Error al enviar correo: {e}", exc_info=True)
                return jsonify({'success': False, 'message': f'Error al enviar correo de validación: {str(e)}'})
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
        
        try:
            mail = current_app.extensions['mail']
            msg = Message('Nuevo código de validación - Coffee Hacienda', 
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[correo_nuevo])
            msg.body = f"""Hola,

Has actualizado tu correo para tu cuenta en Coffee Hacienda.

Tu nuevo código de validación:

{nuevo_codigo}

Expira en 24 horas.

Saludos,
Coffee Hacienda"""
            mail.send(msg)
            return jsonify({'success': True, 'message': 'Correo actualizado correctamente. Se ha enviado un nuevo código de validación.'})
        except Exception as e:
            logger.error(f"Error al enviar correo: {e}", exc_info=True)
            return jsonify({'success': False, 'message': f'Error al enviar correo de validación: {str(e)}'})
        
    except Exception as e:
        logger.error(f"Error al actualizar correo: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
