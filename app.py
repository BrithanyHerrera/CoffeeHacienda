from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.modelsLogin import verificar_usuario
from models.modelsUsuarios import obtener_usuarios, crear_usuario, actualizar_usuario, eliminar_usuario, obtener_usuario_por_id, obtener_roles
from models.modelsProductos import obtener_productos, agregar_producto, actualizar_producto, eliminar_producto
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify

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

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

# Ruta de ejemplo para manejar la solicitud de guardar un producto
@app.route('/api/productos/guardar', methods=['POST'])
@login_required
def guardar_producto():
    try:
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        imagen = request.files.get('imagen')  # Imagen opcional
        imagen_path = None
        
        # Verificar si la imagen fue proporcionada
        if imagen:
            # Asegúrate de guardar la imagen en una carpeta segura
            imagen_filename = secure_filename(imagen.filename)
            imagen_path = os.path.join('static/images', imagen_filename)
            imagen.save(imagen_path)
        
        # Obtener el ID del producto (si existe)
        id_producto = request.form.get('id')
        
        if id_producto:  # Si se está actualizando el producto
            # Lógica para actualizar el producto
            producto = Producto.query.get(id_producto)  # Suponiendo que usas SQLAlchemy para interactuar con la base de datos
            
            if producto:
                # Actualizar el nombre y precio del producto
                producto.nombre = nombre
                producto.precio = precio

                # Si se proporcionó una nueva imagen, actualizar la ruta de la imagen
                if imagen:
                    producto.imagen = imagen_path
                
                # Guardar los cambios
                db.session.commit()
                return jsonify({'success': True, 'message': 'Producto actualizado exitosamente'})
            else:
                return jsonify({'success': False, 'message': 'Producto no encontrado'})

        else:  # Si se está agregando un nuevo producto
            # Lógica para agregar un nuevo producto
            nuevo_producto = Producto(
                nombre=nombre,
                precio=precio,
                imagen=imagen_path if imagen else None  # Si no se proporciona imagen, se guarda como None
            )
            
            # Agregar el nuevo producto a la base de datos
            db.session.add(nuevo_producto)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Producto agregado exitosamente'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al guardar el producto: {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)
