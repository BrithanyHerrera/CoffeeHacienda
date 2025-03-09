# Lista de productos simulada (en un caso real, usarías una base de datos)
productos = []

def obtener_productos():
    return productos

def agregar_producto(nombre, precio, imagen):
    nuevo_producto = {
        'id': len(productos) + 1,
        'nombre': nombre,
        'precio': precio,
        'imagen': imagen
    }
    productos.append(nuevo_producto)
    return True

def actualizar_producto(id, nombre, precio, imagen):
    for producto in productos:
        if producto['id'] == id:
            producto.update({'nombre': nombre, 'precio': precio, 'imagen': imagen})
            return True
    return False

def eliminar_producto(id):
    global productos
    productos = [p for p in productos if p['id'] != id]
    return True