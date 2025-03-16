from bd import Conexion_BD
from pymysql.cursors import DictCursor  # Para evitar errores con dictionary=True

def obtener_productos_menu():
    productos = []
    
    try:
        connection = Conexion_BD()
        if not connection:
            print("No se pudo conectar a la base de datos")
            return productos  # Retorna una lista vacía si no hay conexión
        
        with connection.cursor(DictCursor) as cursor:
            query = """
            SELECT p.id, p.nombre_producto, p.descripcion, p.precio, p.stock, 
                   p.stock_minimo, p.stock_maximo, p.categoria_id, p.ruta_imagen, 
                   c.categoria
            FROM tproductos p 
            LEFT JOIN tcategorias c ON p.categoria_id = c.id
            ORDER BY p.nombre_producto
            """
            cursor.execute(query)
            productos = cursor.fetchall()

        # Obtener variantes para cada producto
        for producto in productos:
            producto["variantes"] = obtener_variantes_menu(producto["id"])

        connection.close()
        
        print("Productos obtenidos de la BD:", productos)  # Depuración
        
    except Exception as e:
        print(f"Error al obtener productos: {e}")  # Depuración
    
    return productos

def obtener_variantes_menu(producto_id):
    variantes = []
    
    try:
        connection = Conexion_BD()
        if not connection:
            print(f"No se pudo conectar a la base de datos para obtener variantes del producto {producto_id}")
            return variantes
        
        with connection.cursor(DictCursor) as cursor:
            query = """
            SELECT t.tamano, pv.precio 
            FROM tproductos_variantes pv
            JOIN ttamanos t ON pv.tamano_id = t.id
            WHERE pv.producto_id = %s
            """
            cursor.execute(query, (producto_id,))
            variantes = cursor.fetchall()
        
        connection.close()
        
    except Exception as e:
        print(f"Error al obtener variantes del producto {producto_id}: {e}")
    
    return variantes
