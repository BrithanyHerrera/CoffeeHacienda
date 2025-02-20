from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def principal():
    return render_template('menu.html')

# Datos de ejemplo
productos = [
    {'id': 1, 'nombre': 'Cappuccino', 'precio': 4.98}
]

@app.route('/productosCRUD')
def listar_productos():
    return render_template('productosCRUD.html', productos=productos)

@app.route('/productosCRUD/agregar', methods=['POST'])
def agregar_producto():
    nuevo_producto = {
        'id': len(productos) + 1,
        'nombre': request.form['nombre'],
        'precio': float(request.form['precio'])
    }
    productos.append(nuevo_producto)
    return redirect(url_for('listar_productos'))

@app.route('/productosCRUD/eliminar/<int:id>')
def eliminar_producto(id):
    global productos
    productos = [p for p in productos if p['id'] != id]
    return redirect(url_for('listar_productos'))

if __name__ == '__main__':
    app.run(debug=True)
