from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.modelsLogin import verificar_usuario
from models.modelsUsuarios import obtener_usuarios, crear_usuario, actualizar_usuario, eliminar_usuario, obtener_usuario_por_id, obtener_roles
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify

app = Flask(__name__)

app.secret_key = 'mi_clave_secreta'  # Cambia esto por una clave segura

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

@app.route('/gestionProductos')
@login_required  # Ruta protegida
def gestion_productos():
    return render_template('gestionProductos.html', productos=productos)

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

# Datos de ejemplo
productos = [
    {'id': 1, 'nombre': 'Cappuccino', 'precio': 4.98}
]

@app.route('/gestionProductos/agregar', methods=['POST'])
@login_required  # Ruta protegida
def agregar_producto():
    nuevo_producto = {
        'id': len(productos) + 1,
        'nombre': request.form['nombre'],
        'precio': float(request.form['precio'])
    }
    productos.append(nuevo_producto)
    return redirect(url_for('gestion_productos'))

@app.route('/gestionProductos/eliminar/<int:id>')
@login_required  # Ruta protegida
def eliminar_producto(id):
    global productos
    productos = [p for p in productos if p['id'] != id]
    return redirect(url_for('gestion_productos'))

if __name__ == '__main__':
    app.run(debug=True)
