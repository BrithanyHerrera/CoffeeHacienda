from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.modelsLogin import verificar_usuario
from models.modelsUsuarios import obtener_usuarios, crear_usuario, actualizar_usuario, eliminar_usuario, obtener_usuario_por_id, obtener_roles ,actualizar_usuario
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify
# Importar las funciones necesarias de modelsProductos
from models.modelsProductos import (obtener_productos, obtener_categorias, obtener_tamanos,
                                   agregar_producto, actualizar_producto, eliminar_producto,
                                   obtener_producto_por_id, agregar_variante_producto,
                                   obtener_variantes_por_producto, actualizar_variante_producto,
                                   eliminar_variantes_producto)
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)

app.secret_key = 'mi_clave_secreta'  # Cambia esto por una clave segura

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
    # Limpiar cualquier sesión existente
    session.clear()
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        usuario_valido = verificar_usuario(usuario, contrasena)
        
        if usuario_valido:
            session['usuario'] = usuario
            session['last_activity'] = datetime.now().isoformat()
            return redirect(url_for('bienvenida'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

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
    return render_template('bienvenida.html')

@app.route('/menu')
@login_required  # Ruta protegida
def menu():
    nombre_usuario = session['usuario']
    return render_template('menu.html', nombre_usuario=nombre_usuario)

@app.route('/finalizarOrden')
@login_required  # Ruta protegida
def finalizarOrden():
    return render_template('finalizarOrden.html')

@app.route('/gestionProductos')
@login_required
def gestion_productos():
    productos = obtener_productos()
    categorias = obtener_categorias()
    tamanos = obtener_tamanos()
    return render_template('gestionProductos.html', productos=productos, categorias=categorias, tamanos=tamanos)

@app.route('/ordenes')
@login_required  # Ruta protegida
def ordenes():
    return render_template('ordenes.html')

@app.route('/historial')
@login_required  # Ruta protegida
def historial():
    return render_template('historial.html')

@app.route('/gestionUsuarios')
@login_required
def gestionUsuarios():
    usuarios = obtener_usuarios()
    roles = obtener_roles()
    return render_template('gestionUsuarios.html', usuarios=usuarios, roles=roles)

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
            resultado, mensaje = crear_usuario(usuario, contrasena, correo, rol_id)
            return jsonify({
                'success': resultado,
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
    if eliminar_usuario(id):
        flash('Usuario eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar usuario', 'danger')
    return redirect(url_for('gestionUsuarios'))

@app.route('/propinas')
@login_required  # Ruta protegida
def propinas():
    return render_template('propinas.html')

@app.route('/corteCaja')
@login_required  # Ruta protegida
def corte():
    return render_template('corteCaja.html')

@app.route('/reporteFinanciero')
@login_required  # Ruta protegida
def reporte():
    return render_template('reportesFinancieros.html')

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

# Ruta para guardar productos
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
        precio = request.form.get('precioProducto')
        stock = request.form.get('stockProducto')
        stock_min = request.form.get('stockMinProducto')
        stock_max = request.form.get('stockMaxProducto')
        categoria_id = request.form.get('categoriaProducto')
        tamano_id = request.form.get('tamanoProducto')
        
        # Manejo de la imagen
        ruta_imagen = None
        if 'imagenProducto' in request.files:
            archivo = request.files['imagenProducto']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                # Crear nombre único para el archivo
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = secure_filename(timestamp + '.' + archivo.filename.rsplit('.', 1)[1].lower())
                
                # Asegurar que el directorio existe
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                # Guardar el archivo
                archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ruta_imagen = f'/static/images/productos/{filename}'
        
        if id_producto:  # Editar producto existente
            # Si no se proporcionó una nueva imagen, mantener la imagen actual
            if not ruta_imagen:
                producto_actual = obtener_producto_por_id(id_producto)
                if producto_actual and producto_actual.get('ruta_imagen'):
                    ruta_imagen = producto_actual['ruta_imagen']
            
            # Verificar si hay cambios en el producto
            producto_actual = obtener_producto_por_id(id_producto)
            if (producto_actual and 
                str(producto_actual['nombre_producto']) == str(nombre) and
                str(producto_actual.get('descripcion', '')) == str(descripcion or '') and
                float(producto_actual['precio']) == float(precio) and
                int(producto_actual['stock']) == int(stock) and
                int(producto_actual.get('stock_minimo', 0)) == int(stock_min) and
                int(producto_actual.get('stock_maximo', 0)) == int(stock_max) and
                int(producto_actual['categoria_id']) == int(categoria_id) and
                producto_actual.get('ruta_imagen') == ruta_imagen):
                # No hay cambios, devolver mensaje informativo
                return jsonify({
                    'success': True,
                    'message': 'No se realizaron cambios en el producto'
                })
                    
            resultado = actualizar_producto(id_producto, nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen)
            mensaje = 'Producto actualizado exitosamente' if resultado else 'Error al actualizar producto'
        else:  # Crear nuevo producto
            resultado = agregar_producto(nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen)
            mensaje = 'Producto creado exitosamente' if resultado else 'Error al crear producto'
            
            # Si se agregó el producto y se especificó un tamaño, agregar la variante
            if resultado and tamano_id:
                # Obtener el ID del producto recién insertado
                nuevo_producto = obtener_productos()[-1]  # Último producto agregado
                agregar_variante_producto(nuevo_producto['Id'], tamano_id, precio)
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        print(f"Error en guardar_producto: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'No se realizaron cambios en el producto. Detalles: {str(e)}'
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

if __name__ == '__main__':
    app.run(debug=True)