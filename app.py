from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from bd import Conexion_BD
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify
from werkzeug.utils import secure_filename
import os
import time

# Importar models
from models.modelsLogin import verificar_usuario
from models.modelsUsuarios import (obtener_usuarios, crear_usuario, actualizar_usuario, 
                                eliminar_usuario, obtener_usuario_por_id, obtener_roles, 
                                actualizar_usuario, obtener_usuario_por_correo,
                                guardar_usuario_pendiente, validar_codigo_usuario,
                                reenviar_codigo_validacion)
from models.modelsProductos import (obtener_productos, obtener_categorias, obtener_tamanos,
                                agregar_producto, actualizar_producto, eliminar_producto,
                                obtener_producto_por_id, agregar_variante_producto,
                                obtener_variantes_por_producto, actualizar_variante_producto,
                                eliminar_variantes_producto)
from models.modelsProductosMenu import obtener_productos_menu
from models.modelsCorteCaja import (filtrar_ventas, guardar_corte_caja, obtener_corte_por_id)
from models.modelsInventario import obtener_productos_inventario, actualizar_stock_producto
from models.modelsHistorial import obtener_historial_ventas, obtener_detalle_venta
from models.modelsVentas import (crear_venta, obtener_cliente_por_nombre, 
                                obtener_ordenes_pendientes, actualizar_estado_orden,
                                obtener_detalle_orden)
from models.modelsRecuperacion import guardar_codigo_recuperacion, verificar_codigo_recuperacion, actualizar_contrasena_por_codigo, generar_codigo_recuperacion
from models.modelsLimpieza import limpiar_validaciones_expiradas, limpiar_codigos_recuperacion_expirados


app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'

# Configuración del correo electrónico
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sanvicente.coffeehacienda@gmail.com'
app.config['MAIL_PASSWORD'] = 'v f e v k x u z m r x n f b h e'
mail = Mail(app)

# Configuración para subida de imágenes
UPLOAD_FOLDER = 'static/images/productos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuración para prevenir el cacheo del navegador
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def login_required(f):
    @wraps(f)
    def wrapped_view(*args, **kwargs):
        # Verificar si el usuario está en la sesión y si la sesión no ha expirado
        if 'usuario' not in session:
            return redirect(url_for('login'))
        
        # Verificar el tiempo de la última actividad
        if 'last_activity' not in session:
            session.clear()
            return redirect(url_for('login'))
        
        # Si han pasado más de 30 minutos desde la última actividad
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.now() - last_activity > timedelta(minutes=30):
            session.clear()
            return redirect(url_for('login'))
        
        # Actualizar el tiempo de última actividad
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    
    return wrapped_view

@app.route('/', methods=['GET', 'POST'])
def login():
    # Limpiar registros expirados
    limpiar_validaciones_expiradas()
    limpiar_codigos_recuperacion_expirados()
    
    # Guardar la bandera antes de limpiar la sesión
    password_reset = 'password_reset' in session
    
    session.clear()  # Limpiar cualquier sesión existente
    
    # Verificar si venía de un restablecimiento de contraseña
    if password_reset:
        flash('Contraseña actualizada correctamente.', 'success')
    
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        if not usuario or not contrasena:
            flash('Por favor, ingrese usuario y contraseña', 'danger')
            return render_template('login.html')
        
        usuario_valido, rol_id = verificar_usuario(usuario, contrasena)
        
        if usuario_valido:
            conn = Conexion_BD()
            cursor = conn.cursor()
            cursor.execute("SELECT rol FROM troles WHERE Id = %s", (rol_id,))
            rol_resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if rol_resultado:
                session['usuario'] = usuario
                session['rol'] = rol_resultado['rol']
                session['last_activity'] = datetime.now().isoformat()
                flash('¡Bienvenido!', 'success')
                return redirect(url_for('bienvenida'))
            else:
                flash('Error al obtener rol de usuario', 'danger')
                return render_template('login.html')
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'Administrador':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('bienvenida'))
        return f(*args, **kwargs)
    return decorated_function

def verificar_usuario(usuario, contrasena):
    conn = Conexion_BD()
    cursor = conn.cursor()
    cursor.execute("SELECT rol_id FROM tusuarios WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if resultado:
        return True, resultado['rol_id']  # Devuelve True y el rol_id
    return False, None  # Devuelve False si no es válido

@app.route('/salir')
def salir():
    session.pop('usuario', None)  # Eliminar al usuario de la sesión
    return redirect(url_for('login'))

@app.route('/sidebar')
@login_required  # Ruta protegida
def sidebar():
    return render_template('sidebar.html')

@app.route('/bienvenida')
@login_required  # Ruta protegida
def bienvenida():
    # Obtener productos con alertas de inventario
    productos = obtener_productos_inventario()
    
    alertas_criticas = 0
    alertas_normales = 0
    
    for producto in productos:
        if producto['stock'] <= producto['stock_minimo'] or producto['stock'] <= producto['stock_minimo'] + 5:
            alertas_criticas += 1
        elif producto['stock'] <= producto['stock_minimo'] + 10:
            alertas_normales += 1
    
    alertas_inventario = alertas_criticas + alertas_normales
    
    return render_template('bienvenida.html', 
                        alertas_inventario=alertas_inventario,
                        alertas_criticas=alertas_criticas,
                        alertas_normales=alertas_normales)

@app.route('/menu')
@login_required  # Ruta protegida
def menu():
    nombre_usuario = session['usuario']
    productos = obtener_productos_menu()
    return render_template('menu.html', nombre_usuario=nombre_usuario, productos=productos)

@app.route('/finalizarOrden')
@login_required  # Ruta protegida
def finalizarOrden():
    return render_template('finalizarOrden.html')

@app.route('/gestionProductos')
@login_required
def gestion_productos():
    productos = obtener_productos()
    # Obtener variantes para cada producto
    for producto in productos:
        producto['variantes'] = obtener_variantes_por_producto(producto['Id'])
    
    categorias = obtener_categorias()
    tamanos = obtener_tamanos()
    
    return render_template('gestionProductos.html', 
                        productos=productos,
                        categorias=categorias,
                        tamanos=tamanos)

@app.route('/inventario')
@login_required
def inventario():
    # Obtener productos que requieren inventario
    productos = obtener_productos_inventario()
    return render_template('inventario.html', productos=productos)


@app.route('/api/inventario/actualizar', methods=['POST'])
@login_required
def actualizar_inventario():
    try:
        data = request.json
        id_producto = data.get('id')
        nuevo_stock = data.get('stock')
        nuevo_stock_min = data.get('stock_min')
        nuevo_stock_max = data.get('stock_max')
        
        # Validar que los valores no sean cero
        if nuevo_stock_min == 0:
            return jsonify({
                'success': False,
                'message': 'El stock mínimo no puede ser cero'
            })
            
        if nuevo_stock_max == 0:
            return jsonify({
                'success': False,
                'message': 'El stock máximo no puede ser cero'
            })
            
        # Validar que el stock mínimo y máximo no sean iguales
        if nuevo_stock_min == nuevo_stock_max:
            return jsonify({
                'success': False,
                'message': 'El stock mínimo y máximo no pueden ser iguales'
            })
        
        # Validar que el stock mínimo no sea mayor que el stock máximo
        if nuevo_stock_min > nuevo_stock_max:
            return jsonify({
                'success': False,
                'message': 'El stock mínimo no puede ser mayor que el stock máximo'
            })
            
        # Validar que el stock máximo no sea menor que el stock mínimo
        if nuevo_stock_max < nuevo_stock_min:
            return jsonify({
                'success': False,
                'message': 'El stock máximo no puede ser menor que el stock mínimo'
            })
        
        # Obtener valores actuales para comparar
        productos = obtener_productos_inventario()
        producto_actual = next((p for p in productos if p['Id'] == int(id_producto)), None)
        
        if not producto_actual:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            })
        
        # Verificar si hay cambios
        if (producto_actual['stock'] == nuevo_stock and 
            producto_actual['stock_minimo'] == nuevo_stock_min and 
            producto_actual['stock_maximo'] == nuevo_stock_max):
            return jsonify({
                'success': True,
                'message': 'No se realizaron cambios en el inventario'
            })
        
        resultado = actualizar_stock_producto(id_producto, nuevo_stock, nuevo_stock_min, nuevo_stock_max)
        
        # Determinar mensaje basado en qué cambió
        mensaje = 'Inventario actualizado correctamente'
        if resultado:
            if producto_actual['stock'] != nuevo_stock and producto_actual['stock_minimo'] == nuevo_stock_min and producto_actual['stock_maximo'] == nuevo_stock_max:
                mensaje = 'Stock actualizado correctamente'
            elif producto_actual['stock'] == nuevo_stock and (producto_actual['stock_minimo'] != nuevo_stock_min or producto_actual['stock_maximo'] != nuevo_stock_max):
                mensaje = 'Límites de stock actualizados correctamente'
        else:
            mensaje = 'Error al actualizar inventario'
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
        

@app.route('/ordenes')
@login_required  # Ruta protegida
def ordenes():
    # Obtener órdenes pendientes
    ordenes_pendientes = obtener_ordenes_pendientes()
    return render_template('ordenes.html', ordenes=ordenes_pendientes)

# Agregar rutas API para gestionar órdenes
@app.route('/api/ordenes', methods=['GET'])
@login_required
def api_obtener_ordenes():
    try:
        ordenes = obtener_ordenes_pendientes()
        return jsonify({
            'success': True,
            'ordenes': ordenes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/ordenes/<int:id>/detalles', methods=['GET'])
@login_required
def api_detalle_orden(id):
    try:
        detalles = obtener_detalle_orden(id)
        if detalles:
            return jsonify({
                'success': True,
                'detalles': detalles
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Orden no encontrada'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/ordenes/<int:id>/estado', methods=['POST'])
@login_required
def api_actualizar_estado_orden(id):
    try:
        data = request.json
        nuevo_estado = data.get('estado')
        
        # Mapear nombres de estado a IDs
        estados = {
            'Pendiente': 1,
            'En proceso': 2,
            'Cancelado': 3,
            'Completado': 4,
            'Reembolsada': 5
        }
        
        if nuevo_estado not in estados:
            return jsonify({
                'success': False,
                'message': 'Estado no válido'
            })
        
        # Obtener el estado actual de la orden
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("SELECT estado_id FROM tventas WHERE Id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not resultado:
            return jsonify({
                'success': False,
                'message': 'Orden no encontrada'
            })
        
        estado_actual_id = resultado['estado_id']
        
        # Definir transiciones válidas
        transiciones_validas = {
            1: [2, 3],           # Pendiente -> En proceso, Cancelado
            2: [3, 4],           # En proceso -> Cancelado, Completado
            3: [],               # Cancelado -> (ninguno)
            4: [],               # Completado -> (ninguno)
            5: []                # Reembolsada -> (ninguno)
        }
        
        # Verificar si la transición es válida
        if estados[nuevo_estado] not in transiciones_validas[estado_actual_id] and estados[nuevo_estado] != estado_actual_id:
            # Obtener nombre del estado actual
            estado_actual_nombre = next((nombre for nombre, id in estados.items() if id == estado_actual_id), "Desconocido")
            
            # Obtener nombres de estados válidos
            estados_validos = [next((nombre for nombre, id in estados.items() if id == estado_id), "Desconocido") 
                            for estado_id in transiciones_validas[estado_actual_id]]
            
            mensaje_estados = ", ".join(estados_validos) if estados_validos else "ninguno"
            
            return jsonify({
                'success': False,
                'message': f'Transición no válida. Desde "{estado_actual_nombre}" solo puede cambiar a: {mensaje_estados}'
            })
        
        # Si el nuevo estado es "Cancelado", eliminar la orden y sus detalles
        if nuevo_estado == 'Cancelado':
            conn = Conexion_BD()
            cursor = conn.cursor()
            
            # Primero eliminar los detalles de la venta (debido a la restricción de clave foránea)
            cursor.execute("DELETE FROM tdetalleventas WHERE venta_id = %s", (id,))
            
            # Luego eliminar la venta
            cursor.execute("DELETE FROM tventas WHERE Id = %s", (id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Orden cancelada y eliminada del sistema'
            })
        else:
            # Si no es cancelación, actualizar el estado normalmente
            resultado = actualizar_estado_orden(id, estados[nuevo_estado])
            
            if resultado:
                return jsonify({
                    'success': True,
                    'message': f'Estado actualizado a {nuevo_estado}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error al actualizar estado'
                })
    except Exception as e:
        print(f"Error al actualizar estado de orden: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/historial')
@login_required  # Ruta protegida
def historial():
    # Obtener la lista de vendedores para el filtro
    conn = Conexion_BD()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT usuario FROM tusuarios ORDER BY usuario")
    vendedores = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('historial.html', vendedores=vendedores)

@app.route('/gestionUsuarios')
@login_required
def gestionUsuarios():
    usuarios = obtener_usuarios()
    roles = obtener_roles()
    return render_template('gestionUsuarios.html', usuarios=usuarios, roles=roles, rol=session.get('rol'))

# Agregar nuevas rutas para manejar solicitudes AJAX
@app.route('/api/usuarios/guardar', methods=['POST'])
@login_required
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
                    msg = Message('Validación de cuenta - Coffee Hacienda', 
                                sender=app.config['MAIL_USERNAME'],
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


@app.route('/gestionUsuarios/eliminar/<int:id>')
@login_required
def eliminar_usuario_route(id):
    try:
        if eliminar_usuario(id):
            return jsonify({
                'success': True,
                'message': 'Usuario eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al eliminar usuario'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/propinas')
@login_required  # Ruta protegida
def propinas():
    return render_template('propinas.html')

@app.route('/filtrarVentas', methods=['POST'])
def filtrar_ventas_route():
    return filtrar_ventas()

@app.route('/corteCaja', methods=['GET', 'POST'])
@login_required  # Ruta protegida para asegurar que solo los usuarios logueados puedan acceder
def corte():
    nombre_usuario = session['usuario']
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario (no JSON)
            fecha_inicio = request.form.get('fecha_hora_inicio')
            fecha_cierre = request.form.get('fecha_hora_cierre')
            total_ventas = float(request.form.get('total_ventas', 0))
            total_efectivo = float(request.form.get('total_efectivo', 0))
            total_transferencias = float(request.form.get('total_transferencias', 0))
            total_paypal = float(request.form.get('total_paypal', 0))
            total_contado = float(request.form.get('total_contado', 0))
            pagos_realizados = float(request.form.get('pagos_realizados', 0))

            # Obtener el ID del vendedor desde la sesión
            vendedor_id = session.get('usuario_id')

            # Llamar a la función de modelo para guardar el corte de caja en la base de datos
            resultado, error = guardar_corte_caja(
                vendedor_id, fecha_inicio, fecha_cierre,
                total_ventas, total_efectivo,
                total_transferencias, total_paypal,
                total_contado, pagos_realizados
            )

            if resultado:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": error})

        except Exception as e:
            return jsonify({"success": False, "error": f"Error al guardar el corte: {str(e)}"}), 500

    # Si es un GET, simplemente mostrar la página de corte
    totales = filtrar_ventas()  # Obtener los totales de las venta

    conexion = Conexion_BD()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT fecha_hora_cierre, fondo, total_contado, total_ventas, pagos_realizados
            FROM TCortesCaja
            ORDER BY fecha_hora_cierre DESC
        """)
        cortes = cursor.fetchall()

    return render_template('corteCaja.html', totales=totales, cortes=cortes, nombre_usuario=nombre_usuario)

@app.route('/api/corteCaja/<int:id>', methods=['GET'])
@login_required
def get_corte_caja(id):
    try:
        corte = obtener_corte_por_id(id)
        if corte:
            return jsonify({
                'success': True,
                'corte': corte
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Corte de caja no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/guardarCorteCaja', methods=['POST'])
@login_required
def guardar_corte():
    try:
        data = request.get_json()  # o request.json si lo mandas en formato JSON
        print("Datos recibidos:", data)

        vendedor_id = session.get('usuario_id')  # o session['nombre_usuario'] si usas el nombre

        # Recolectar los datos enviados desde el formulario o JS
        fecha_inicio = data.get('fecha_hora_inicio')
        fecha_cierre = data.get('fecha_hora_cierre')
        total_ventas = float(data.get('total_ventas', 0))
        total_efectivo = float(data.get('total_efectivo', 0))
        total_transferencias = float(data.get('total_transferencias', 0))
        total_paypal = float(data.get('total_paypal', 0))
        total_contado = float(data.get('total_contado', 0))
        pagos_realizados = float(data.get('pagos_realizados', 0))
        fondo = float(data.get('fondo', 0))

        # Guardar el corte en la base de datos
        exito = guardar_corte_caja(
            vendedor_id, fecha_inicio, fecha_cierre,
            total_ventas, total_efectivo,
            total_transferencias, total_paypal, total_contado,
            pagos_realizados, fondo
        )

        if exito:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al guardar el corte"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": f"Error en la ruta /guardarCorteCaja: {str(e)}"}), 500 



@app.route('/reporteFinanciero')
@login_required  # Ruta protegida
def reporte():
    conexion = Conexion_BD()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT fecha_hora_cierre, fondo, total_contado, total_ventas, pagos_realizados, ganancia_o_perdida
            FROM TCortesCaja
            ORDER BY fecha_hora_cierre DESC
        """)
        cortes = cursor.fetchall()


    return render_template('reportesFinancieros.html', cortes=cortes)

# Agregar rutas API para obtener categorías y tamaños
@app.route('/api/categorias', methods=['GET'])
@login_required
def get_categorias():
    try:
        categorias = obtener_categorias()
        return jsonify({
            'success': True,
            'categorias': categorias
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/tamanos', methods=['GET'])
@login_required
def get_tamanos():
    try:
        tamanos = obtener_tamanos()
        return jsonify({
            'success': True,
            'tamanos': tamanos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/productos/guardar', methods=['POST'])
@login_required
def guardar_producto():
    try:
        # Print form data for debugging
        print("Form data:", request.form)
        print("Files:", request.files)
        
        id_producto = request.form.get('id')
        nombre = request.form.get('nombreProducto')
        descripcion = request.form.get('descripcionProducto')
        precio = float(request.form.get('precioProducto'))
        stock = int(request.form.get('stockProducto') or 0)
        stock_min = int(request.form.get('stockMinProducto') or 0)
        stock_max = int(request.form.get('stockMaxProducto') or 0)
        categoria_id = int(request.form.get('categoriaProducto'))
        tamano_id = int(request.form.get('tamano_id'))
        
        # Manejar la imagen
        ruta_imagen = None
        if 'imagenProducto' in request.files:
            archivo = request.files['imagenProducto']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = secure_filename(timestamp + '.' + archivo.filename.rsplit('.', 1)[1].lower())
                
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ruta_imagen = f'/static/images/productos/{filename}'
        
        if id_producto:  # Editar producto existente
            producto_actual = obtener_producto_por_id(id_producto)
            
            if not ruta_imagen and producto_actual and producto_actual.get('ruta_imagen'):
                ruta_imagen = producto_actual['ruta_imagen']
            
            # Actualizar el producto principal
            resultado, mensaje = actualizar_producto(
                id_producto, nombre, descripcion, precio, 
                stock, stock_min, stock_max, categoria_id, ruta_imagen
            )
            
            # Manejar la variante del tamaño
            if tamano_id and tamano_id != 4:  # 4 es "No Aplica"
                # Eliminar todas las variantes existentes primero
                eliminar_variantes_producto(id_producto)
                # Crear nueva variante con el tamaño seleccionado
                agregar_variante_producto(id_producto, tamano_id, precio)
            elif tamano_id == 4:  # Si seleccionó "No Aplica"
                eliminar_variantes_producto(id_producto)
        else:  # Crear nuevo producto
            resultado, nuevo_id = agregar_producto(
                nombre, descripcion, precio, stock, 
                stock_min, stock_max, categoria_id, ruta_imagen
            )
            
            if resultado and tamano_id and tamano_id != 4:
                agregar_variante_producto(nuevo_id, tamano_id, precio)
                
            mensaje = 'Producto creado exitosamente' if resultado else 'Error al crear producto'
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        print(f"Error en guardar_producto: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/api/productos/eliminar', methods=['POST'])
@login_required
def eliminar_producto_route():
    try:
        data = request.json
        id_producto = data.get('id')
        
        # Primero eliminar las variantes asociadas
        eliminar_variantes_producto(id_producto)
        
        # Luego eliminar el producto
        resultado = eliminar_producto(id_producto)
        
        return jsonify({
            'success': resultado,
            'message': 'Producto eliminado exitosamente' if resultado else 'Error al eliminar producto'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/productos/variantes', methods=['POST'])
@login_required
def guardar_variante():
    try:
        data = request.json
        producto_id = data.get('producto_id')
        tamano_id = data.get('tamano_id')
        precio = data.get('precio')
        
        resultado = agregar_variante_producto(producto_id, tamano_id, precio)
        
        return jsonify({
            'success': resultado,
            'message': 'Variante agregada exitosamente' if resultado else 'Error al agregar variante'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/productos/variantes/<int:producto_id>', methods=['GET'])
@login_required
def obtener_variantes(producto_id):
    try:
        variantes = obtener_variantes_por_producto(producto_id)
        
        return jsonify({
            'success': True,
            'variantes': variantes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/usuarios/<int:id>', methods=['GET'])
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

@app.route('/api/productos/<int:id>', methods=['GET'])
@login_required
def get_producto(id):
    try:
        producto = obtener_producto_por_id(id)
        if producto:
            # Obtener también las variantes del producto
            variantes = obtener_variantes_por_producto(id)
            return jsonify({
                'success': True,
                'producto': producto,
                'variantes': variantes
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/categorias/<int:id>', methods=['GET'])
@login_required
def get_categoria(id):
    try:
        categorias = obtener_categorias()
        categoria = next((cat for cat in categorias if cat['Id'] == id), None)
        
        if categoria:
            return jsonify({
                'success': True,
                'categoria': categoria
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Categoría no encontrada'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/historial-ventas')
@login_required
def historial_ventas():
    return render_template('historial.html')

@app.route('/api/historial-ventas', methods=['GET'])
@login_required
def api_historial_ventas():
    filtro_cliente = request.args.get('cliente', '')
    filtro_vendedor = request.args.get('vendedor', '')
    fecha_inicio = request.args.get('fechaInicio', '')
    fecha_fin = request.args.get('fechaFin', '')

    try:
        ventas = obtener_historial_ventas(filtro_cliente, fecha_inicio, fecha_fin)
        return jsonify({'success': True, 'ventas': ventas})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/historial-ventas/<int:id>', methods=['GET'])
@login_required
def api_detalle_venta(id):
    try:
        # Obtener detalles básicos de la venta
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Consulta para obtener información principal de la venta
        cursor.execute("""
            SELECT 
                v.Id, 
                v.total, 
                v.fecha_hora, 
                v.numero_mesa,
                c.nombre AS cliente,
                u.usuario AS vendedor,
                mp.tipo_de_pago AS metodo_pago,
                v.total AS dinero_recibido,
                v.total AS cambio  -- Aquí deberías ajustar según tu lógica de negocio
            FROM tventas v
            LEFT JOIN tclientes c ON v.cliente_id = c.Id
            LEFT JOIN tusuarios u ON v.vendedor_id = u.Id
            LEFT JOIN tmetodospago mp ON v.metodo_pago_id = mp.Id
            WHERE v.Id = %s
        """, (id,))
        venta = cursor.fetchone()
        
        if not venta:
            return jsonify({'success': False, 'message': 'Venta no encontrada'})
        
        # Obtener detalles de los productos vendidos
        cursor.execute("""
            SELECT 
                p.nombre_producto,
                pv.precio,
                t.tamano,
                dv.cantidad,
                (dv.precio * dv.cantidad) AS subtotal
            FROM tdetalleventas dv
            JOIN tproductos p ON dv.producto_id = p.Id
            LEFT JOIN tproductos_variantes pv ON dv.producto_id = pv.producto_id
            LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
            WHERE dv.venta_id = %s
        """, (id,))
        detalles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'venta': venta,
            'detalles': detalles
        })
    except Exception as e:
        print(f"Error al obtener detalles de venta: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


# Ruta para procesar ventas desde el menú
@app.route('/api/ventas/crear', methods=['POST'])
@login_required
def procesar_venta():
    try:
        data = request.json
        print("Datos recibidos:", data)
        
        nombre_cliente = data.get('cliente', 'Cliente General')
        numero_mesa = data.get('mesa', '')
        productos = data.get('productos', [])
        total = data.get('total', 0)
        metodo_pago_id = data.get('metodo_pago', 1)
        
        if not productos:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron productos'
            })
            
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        productos_validos = []
        productos_invalidos = []
        productos_sin_stock = []
        
        for producto in productos:
            producto_id = int(producto['id'])
            cantidad_solicitada = int(producto['cantidad'])
            
            # Verificar producto y su categoría
            cursor.execute("""
                SELECT p.Id, p.nombre_producto, p.stock, c.requiere_inventario, c.categoria
                FROM tproductos p
                JOIN tcategorias c ON p.categoria_id = c.id
                WHERE p.Id = %s
            """, (producto_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                # Solo verificar stock si requiere inventario o es Postre/Snack
                requiere_stock = resultado['requiere_inventario'] == 1 or resultado['categoria'] in ['Postre', 'Snack']
                
                if requiere_stock and resultado['stock'] < cantidad_solicitada:
                    productos_sin_stock.append({
                        'id': producto_id,
                        'nombre': resultado['nombre_producto'],
                        'stock_actual': resultado['stock'],
                        'cantidad_solicitada': cantidad_solicitada
                    })
                else:
                    productos_validos.append({
                        'id': producto_id,
                        'cantidad': cantidad_solicitada,
                        'precio': float(producto['precio'])
                    })
            else:
                productos_invalidos.append(producto_id)
                print(f"Producto con ID {producto_id} no encontrado en la base de datos")
        
        cursor.close()
        conn.close()
        
        if productos_sin_stock:
            mensaje_error = "No hay suficiente stock para los siguientes productos:\n"
            for p in productos_sin_stock:
                mensaje_error += f"- {p['nombre']}: Stock actual: {p['stock_actual']}, Solicitado: {p['cantidad_solicitada']}\n"
            
            return jsonify({
                'success': False,
                'message': mensaje_error,
                'productos_sin_stock': productos_sin_stock
            })
        
        if productos_invalidos:
            return jsonify({
                'success': False,
                'message': f'Los siguientes productos no existen en la base de datos: {productos_invalidos}'
            })
            
        # Resto del código para procesar la venta...
        cliente_id = obtener_cliente_por_nombre(nombre_cliente)
        usuario_actual = session.get('usuario', '')
        
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM tusuarios WHERE usuario = %s", (usuario_actual,))
        usuario_db = cursor.fetchone()
        cursor.close()
        conn.close()
        
        vendedor_id = usuario_db['Id'] if usuario_db else 1
        
        if productos_validos:
            conn = Conexion_BD()
            cursor = conn.cursor()
            cursor.execute("SELECT Id FROM testadosventa LIMIT 1")
            estado_result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            estado_id = estado_result['Id'] if estado_result else 4
            
            print(f"Usando estado_id: {estado_id}")
            
            exito, venta_id = crear_venta(cliente_id, vendedor_id, total, productos_validos, metodo_pago_id, numero_mesa, estado_id)
            
            if exito:
                return jsonify({
                    'success': True,
                    'message': 'Venta registrada exitosamente',
                    'venta_id': venta_id
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error al registrar la venta'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'No hay productos válidos para registrar la venta'
            })
    except Exception as e:
        print(f"Error al procesar venta: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al registrar la venta: {str(e)}'
        })
        
@app.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
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
                msg = Message('Recuperación de Contraseña - Coffee Hacienda',
                            sender=app.config['MAIL_USERNAME'],
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
                
            return redirect(url_for('verificar_codigo'))
        else:
            flash('El correo electrónico no está registrado en nuestro sistema. Por favor, verifica el correo.', 'danger')
    
    return render_template('recuperarContrasena.html')

@app.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    # Check if email is in session
    if 'reset_email' not in session:
        flash('Por favor, inicie el proceso de recuperación nuevamente', 'danger')
        return redirect(url_for('recuperar_contrasena'))
        
    if request.method == 'POST':
        codigo = request.form['codigo']
        correo = session['reset_email']
        
        usuario = obtener_usuario_por_correo(correo)
        if usuario and verificar_codigo_recuperacion(usuario['Id'], codigo):
            return redirect(url_for('actualizar_contrasena'))
        else:
            flash('Código inválido o expirado', 'danger')
    
    return render_template('verificarCodigo.html')

@app.route('/actualizar-contrasena', methods=['GET', 'POST'])
def actualizar_contrasena():
    if 'reset_email' not in session:
        return redirect(url_for('recuperar_contrasena'))
        
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
            return redirect(url_for('login'))
        else:
            flash('Error al actualizar la contraseña', 'danger')
    
    return render_template('actualizarContrasena.html')


@app.route('/validar-usuario')
def validar_usuario_view():
    correo = request.args.get('email', '')
    return render_template('validar_usuario.html', correo=correo)

@app.route('/api/usuarios/validar', methods=['POST'])
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

@app.route('/api/usuarios/reenviar-codigo', methods=['POST'])
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
                msg = Message('Nuevo código de validación - Coffee Hacienda', 
                            sender=app.config['MAIL_USERNAME'],
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

@app.route('/api/usuarios/actualizar-correo', methods=['POST'])
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
            msg = Message('Nuevo código de validación - Coffee Hacienda', 
                        sender=app.config['MAIL_USERNAME'],
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

if __name__ == '__main__':
    app.run(debug=True)