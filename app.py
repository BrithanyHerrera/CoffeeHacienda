from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

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

@app.route('/gestionProductos')
def gestion_productos():
    return render_template('gestionProductos.html', productos=productos)

@app.route('/ordenes')
def ordenes():
    return render_template('ordenes.html')

@app.route('/historial')
def historial():
    return render_template('historial.html')

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

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
