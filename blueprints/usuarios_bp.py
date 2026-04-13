from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_mail import Message
from datetime import datetime
from bd import Conexion_BD
from utils import login_required, admin_required, reactivar_usuario
from models.modelsUsuarios import (obtener_usuarios, crear_usuario, actualizar_usuario, 
                                obtener_usuario_por_id, obtener_roles, 
                                obtener_usuario_por_correo,
                                guardar_usuario_pendiente, validar_codigo_usuario,
                                reenviar_codigo_validacion)
from models.modelsRecuperacion import generar_codigo_recuperacion

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/gestionUsuarios')
@login_required
@admin_required
def gestionUsuarios():
    # Obtener usuarios activos
    conn = Conexion_BD()
    cursor = conn.cursor()
    
    # Usuarios activos (activo = 1)
    cursor.execute("""
        SELECT u.Id, u.usuario, u.correo, r.rol, r.Id as rol_id, u.creado_en 
        FROM tusuarios u 
        JOIN troles r ON u.rol_id = r.Id
        WHERE u.activo = 1
        ORDER BY u.usuario
    """)
    usuarios_activos = cursor.fetchall()
    
    # Usuarios inactivos (activo = 0)
    cursor.execute("""
        SELECT u.Id, u.usuario, u.correo, r.rol, r.Id as rol_id, 
               u.creado_en, u.modificado_en
        FROM tusuarios u 
        JOIN troles r ON u.rol_id = r.Id
        WHERE u.activo = 0
        ORDER BY u.modificado_en DESC
    """)
    usuarios_inactivos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
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
        
        # Validar datos
        if not usuario or not correo or not rol_id:
            return jsonify({
                'success': False,
                'message': 'Faltan datos obligatorios'
            })
        
        if id_usuario:  # Editar usuario existente
            # Si no se proporciona nueva contraseña, mantener la actual
            if not contrasena:
                usuario_actual = obtener_usuario_por_id(id_usuario)
                contrasena = usuario_actual['contrasena']
                
            resultado, mensaje = actualizar_usuario(id_usuario, usuario, contrasena, correo, rol_id)
            return jsonify({
                'success': resultado,
                'message': mensaje
            })
        else:  # Crear nuevo usuario
            # En lugar de crear directamente, guardar pendiente de validación
            if not contrasena:
                return jsonify({
                    'success': False,
                    'message': 'La contraseña es obligatoria para nuevos usuarios'
                })
                
            resultado, mensaje, datos = guardar_usuario_pendiente(usuario, contrasena, correo, rol_id)
            
            if resultado:
                # Enviar correo con código de validación
                try:
                    mail = current_app.extensions['mail']
                    msg = Message('Validación de cuenta - Coffee Hacienda', 
                                sender=current_app.config['MAIL_USERNAME'],
                                recipients=[correo])
                    
                    msg.body = f"""
                    Hola {usuario},
                    
                    Gracias por registrarte en Coffee Hacienda. Para completar tu registro, 
                    por favor ingresa el siguiente código de validación:
                    
                    {datos['codigo']}
                    
                    Este código expirará en 30 minutos.
                    
                    Si no solicitaste esta cuenta, puedes ignorar este correo.
                    
                    Saludos,
                    El equipo de Coffee Hacienda
                    """
                    
                    mail.send(msg)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Se ha enviado un código de validación a tu correo electrónico',
                        'require_validation': True,
                        'email': correo
                    })
                except Exception as e:
                    print(f"Error al enviar correo: {e}")
                    return jsonify({
                        'success': False,
                        'message': f'Error al enviar correo de validación: {str(e)}'
                    })
            else:
                return jsonify({
                    'success': False,
                    'message': mensaje
                })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }) 

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['GET'])
@login_required
def get_usuario(id):
    try:
        usuario = obtener_usuario_por_id(id)
        if usuario:
            return jsonify({
                'success': True,
                'usuario': usuario
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@usuarios_bp.route('/gestionUsuarios/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario_route(id):
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT Id FROM tusuarios WHERE Id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            })
        
        # Actualizar el campo activo a False (0) en lugar de eliminar
        cursor.execute("UPDATE tusuarios SET activo = 0 WHERE Id = %s", (id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario desactivado exitosamente'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al desactivar usuario: {str(e)}'
        })
    finally:
        cursor.close()
        conn.close()

@usuarios_bp.route('/gestionUsuarios/activar/<int:id>', methods=['POST'])
@login_required
@admin_required
def activar_usuario_route(id):
    try:
        resultado = reactivar_usuario(id)
        if resultado:
            return jsonify({
                'success': True,
                'message': 'Usuario reactivado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al reactivar usuario'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

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
            return jsonify({
                'success': False,
                'message': 'Faltan datos obligatorios'
            })
        
        resultado, mensaje = validar_codigo_usuario(correo, codigo)
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@usuarios_bp.route('/api/usuarios/reenviar-codigo', methods=['POST'])
def reenviar_codigo_api():
    try:
        data = request.json
        correo = data.get('correo')
        
        if not correo:
            return jsonify({
                'success': False,
                'message': 'El correo electrónico es obligatorio'
            })
        
        resultado, mensaje, codigo = reenviar_codigo_validacion(correo)
        
        if resultado:
            # Enviar correo con el nuevo código
            try:
                mail = current_app.extensions['mail']
                msg = Message('Nuevo código de validación - Coffee Hacienda', 
                            sender=current_app.config['MAIL_USERNAME'],
                            recipients=[correo])
                
                msg.body = f"""
                Hola,
                
                Has solicitado un nuevo código de validación para tu cuenta en Coffee Hacienda.
                
                Tu nuevo código es:
                
                {codigo}
                
                Este código expirará en 24 horas.
                
                Si no solicitaste este código, puedes ignorar este correo.
                
                Saludos,
                El equipo de Coffee Hacienda
                """
                
                mail.send(msg)
                
                return jsonify({
                    'success': True,
                    'message': 'Se ha enviado un nuevo código de validación a tu correo electrónico'
                })
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error al enviar correo de validación: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'message': mensaje
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@usuarios_bp.route('/api/usuarios/actualizar-correo', methods=['POST'])
def actualizar_correo_validacion():
    try:
        data = request.json
        correo_anterior = data.get('correo_anterior')
        correo_nuevo = data.get('correo_nuevo')
        
        if not correo_anterior or not correo_nuevo:
            return jsonify({
                'success': False,
                'message': 'Faltan datos obligatorios'
            })
        
        # Verificar si el nuevo correo ya existe en usuarios
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Id FROM tusuarios WHERE correo = %s", (correo_nuevo,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Ya existe un usuario con ese correo electrónico'
            })
        
        # Verificar si el correo anterior existe en la tabla de validación
        cursor.execute("""
            SELECT id, usuario, contrasena, rol_id
            FROM tvalidacion_usuarios
            WHERE correo = %s AND validado = FALSE
        """, (correo_anterior,))
        
        validacion = cursor.fetchone()
        
        if not validacion:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No se encontró una solicitud pendiente para este correo'
            })
        
        # Generar nuevo código
        nuevo_codigo = generar_codigo_recuperacion()
        
        # Actualizar el correo y el código
        cursor.execute("""
            UPDATE tvalidacion_usuarios
            SET correo = %s, codigo = %s, fecha_creacion = %s
            WHERE id = %s
        """, (correo_nuevo, nuevo_codigo, datetime.now(), validacion['id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Enviar correo con el nuevo código
        try:
            mail = current_app.extensions['mail']
            msg = Message('Nuevo código de validación - Coffee Hacienda', 
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[correo_nuevo])
            
            msg.body = f"""
            Hola,
            
            Has actualizado tu correo electrónico para tu cuenta en Coffee Hacienda.
            
            Tu nuevo código de validación es:
            
            {nuevo_codigo}
            
            Este código expirará en 24 horas.
            
            Si no solicitaste este cambio, puedes ignorar este correo.
            
            Saludos,
            El equipo de Coffee Hacienda
            """
            
            mail.send(msg)
            
            return jsonify({
                'success': True,
                'message': 'Correo actualizado correctamente. Se ha enviado un nuevo código de validación.'
            })
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return jsonify({
                'success': False,
                'message': f'Error al enviar correo de validación: {str(e)}'
            })
        
    except Exception as e:
        print(f"Error al actualizar correo: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
