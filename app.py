from flask import Flask, render_template, request, redirect, url_for, flash
from bd import Conexion_BD
from models.models_login import verificar_usuario
import logging

app = Flask(__name__)

app.secret_key = 'mi_clave_secreta'  # Cambia esto por una clave segura
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        # Verificar usuario y contraseña con la base de datos
        usuario_valido = verificar_usuario(usuario, contrasena)
        
        if usuario_valido:
            # Si el usuario es válido, redirigir a la página principal
            return redirect(url_for('bienvenida'))
        else:
            # Si no es válido, mostrar mensaje de error
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))  # Volver al login
    
    return render_template('login.html')  # Mostrar el formulario de login

@app.route('/salir')
def salir():
    return redirect(url_for('login'))

@app.route('/sidebar')
def sidebar():
    return render_template('sidebar.html')

@app.route('/bienvenida')
def bienvenida():
    return render_template('bienvenida.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/finalizarOrden')
def finalizarOrden():
    return render_template('finalizarOrden.html')

@app.route('/gestionProductos')
def gestion_productos():
    return render_template('gestionProductos.html', productos=productos)

@app.route('/ordenes')
def ordenes():
    return render_template('ordenes.html')

@app.route('/historial')
def historial():
    return render_template('historial.html')

@app.route('/gestionUsuarios')
def gestionUsuarios():
    return render_template('gestionUsuarios.html')

@app.route('/propinas')
def propinas():
    return render_template('propinas.html')

# Datos de ejemplo
productos = [
    {'id': 1, 'nombre': 'Cappuccino', 'precio': 4.98}
]

@app.route('/gestionProductos/agregar', methods=['POST'])
def agregar_producto():
    nuevo_producto = {
        'id': len(productos) + 1,
        'nombre': request.form['nombre'],
        'precio': float(request.form['precio'])
    }
    productos.append(nuevo_producto)
    return redirect(url_for('gestion_productos'))

@app.route('/gestionProductos/eliminar/<int:id>')
def eliminar_producto(id):
    global productos
    productos = [p for p in productos if p['id'] != id]
    return redirect(url_for('gestion_productos'))

if __name__ == '__main__':
    app.run(debug=True)
