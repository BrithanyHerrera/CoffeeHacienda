from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/sidebar')
def sidebar():
    return render_template('sidebar.html')

@app.route('/paginaPrincipal')
def paginaPrincipal():
    return render_template('paginaPrincipal.html')

@app.route('/menu')
def principal():
    return render_template('menu.html')

@app.route('/finalizarOrden')
def finalizar_orden():
    return render_template('finalizarOrden.html')

# Datos de ejemplo
productos = [
    {'id': 1, 'nombre': 'Cappuccino', 'precio': 4.98}
]

@app.route('/gestionProductos')
def gestionProductos():
    return render_template('gestionProductos.html', productos=productos)

@app.route('/gestionProductos/agregar', methods=['POST'])
def agregar_producto():
    nuevo_producto = {
        'id': len(productos) + 1,
        'nombre': request.form['nombre'],
        'precio': float(request.form['precio'])
    }
    productos.append(nuevo_producto)
    return redirect(url_for('listar_productos'))

@app.route('/gestionProductos/eliminar/<int:id>')
def eliminar_producto(id):
    global productos
    productos = [p for p in productos if p['id'] != id]
    return redirect(url_for('listar_productos'))

if __name__ == '__main__':
    app.run(debug=True)
