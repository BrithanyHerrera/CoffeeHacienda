from bd import Conexion_BD
from pymysql.cursors import DictCursor  # Para evitar errores con dictionary=True

def obtener_productos_menu():
    productos = []
    
    try:
        connection = Conexion_BD()
        if not connection:
            print("No se pudo conectar a la base de datos")
            return productos
        
        with connection.cursor(DictCursor) as cursor:
            # Obtener productos
            query_productos = """
            SELECT p.id, p.nombre_producto, p.descripcion, p.precio, p.stock,
                   p.stock_minimo, p.stock_maximo, p.categoria_id, p.ruta_imagen, 
                   c.categoria, c.requiere_inventario
            FROM tproductos p 
            LEFT JOIN tcategorias c ON p.categoria_id = c.id
            WHERE p.activo = 1
            ORDER BY p.nombre_producto
            """
            cursor.execute(query_productos)
            productos = cursor.fetchall()
            
            if productos:
                # Obtener TODAS las variantes en una sola consulta
                producto_ids = [p['id'] for p in productos]
                placeholders = ', '.join(['%s'] * len(producto_ids))
                query_variantes = f"""
                SELECT pv.producto_id, t.tamano, pv.precio 
                FROM tproductos_variantes pv
                JOIN ttamanos t ON pv.tamano_id = t.id
                WHERE pv.producto_id IN ({placeholders})
                """
                cursor.execute(query_variantes, producto_ids)
                todas_variantes = cursor.fetchall()
                
                # Agrupar variantes por producto_id
                variantes_por_producto = {}
                for v in todas_variantes:
                    pid = v['producto_id']
                    if pid not in variantes_por_producto:
                        variantes_por_producto[pid] = []
                    variantes_por_producto[pid].append({'tamano': v['tamano'], 'precio': v['precio']})
                
                # Asignar variantes a cada producto
                for producto in productos:
                    producto["variantes"] = variantes_por_producto.get(producto["id"], [])

        connection.close()
        
    except Exception as e:
        print(f"Error al obtener productos: {e}")
    
    return productos

