from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models.modelsLogin import verificar_usuario
from models.modelsUsuarios import obtener_usuarios, crear_usuario, actualizar_usuario, eliminar_usuario, obtener_usuario_por_id, obtener_roles
from models.modelsProductos import obtener_productos, agregar_producto, actualizar_producto, eliminar_producto, obtener_producto_por_id, obtener_categorias
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify
import os 

app = Flask(__name__)

app.secret_key = 'mi_clave_secreta'  # Cambia esto por una clave segura

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)


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
    return render_template('menu.html')

@app.route('/finalizarOrden')
@login_required  # Ruta protegida
def finalizarOrden():
    return render_template('finalizarOrden.html')

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

# Eliminar o comentar las rutas existentes para agregar/editar usuario
# @app.route('/gestionUsuarios/agregar', methods=['GET', 'POST'])
# @app.route('/gestionUsuarios/editar/<int:id>', methods=['GET', 'POST'])

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
                
            resultado = actualizar_usuario(id_usuario, usuario, contrasena, correo, rol_id)
            mensaje = 'Usuario actualizado exitosamente' if resultado else 'Error al actualizar usuario'
        else:  # Crear nuevo usuario
            resultado = crear_usuario(usuario, contrasena, correo, rol_id)
            mensaje = 'Usuario creado exitosamente' if resultado else 'Error al crear usuario'
        
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

@app.route('/gestionProductos')
@login_required
def gestion_productos():
    return render_template('gestionProductos.html', productos=obtener_productos())

@app.route('/api/categorias')
@login_required
def obtener_categorias_api():
    try:
        categorias = obtener_categorias()
        return jsonify({'success': True, 'categorias': categorias})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/productos/eliminar', methods=['POST'])
@login_required
def eliminar_producto_route():
    try:
        data = request.json
        producto_id = data.get('id')
        
        if eliminar_producto(producto_id):
            return jsonify({'success': True, 'message': 'Producto eliminado exitosamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al eliminar producto'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/productos/guardar', methods=['POST'])
@login_required
def guardar_producto():
    try:
        # Obtener los datos del formulario
        id_producto = request.form.get('id')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        stock_min = int(request.form.get('stockMin', 10))
        stock_max = int(request.form.get('stockMax', 100))
        categoria_id = int(request.form.get('categoria'))
        
        # Manejar la imagen si se proporciona
        imagen = request.files.get('imagen')
        ruta_imagen = None
        
        if imagen and imagen.filename and allowed_file(imagen.filename):
            # Crear un nombre de archivo seguro
            filename = secure_filename(imagen.filename)
            # Añadir timestamp para evitar duplicados
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{filename}"
            # Ruta completa para guardar
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            # Guardar la imagen
            imagen.save(filepath)
            # Ruta relativa para la base de datos
            ruta_imagen = f"/{UPLOAD_FOLDER}/{filename}"
        
        if id_producto:  # Actualizar producto existente
            # Si no hay nueva imagen, mantener la actual
            if not ruta_imagen:
                resultado = actualizar_producto(
                    id_producto, nombre, descripcion, precio, stock, 
                    stock_min, stock_max, categoria_id
                )
            else:
                resultado = actualizar_producto(
                    id_producto, nombre, descripcion, precio, stock, 
                    stock_min, stock_max, categoria_id, ruta_imagen
                )
            
            mensaje = 'Producto actualizado exitosamente' if resultado else 'Error al actualizar producto'
        else:  # Crear nuevo producto
            resultado = agregar_producto(
                nombre, descripcion, precio, stock, 
                stock_min, stock_max, categoria_id, ruta_imagen
            )
            mensaje = 'Producto agregado exitosamente' if resultado else 'Error al agregar producto'
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al guardar el producto: {str(e)}'
        })


# Configuración para guardar imágenes
UPLOAD_FOLDER = 'static/images/productos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Asegurarse de que el directorio de carga existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import request, jsonify
from werkzeug.utils import secure_filename  # Movemos esta importación aquí

# Eliminar la segunda definición de la ruta '/api/productos/guardar'
# y la función guardar_producto duplicada

if __name__ == '__main__':
    app.run(debug=True)
