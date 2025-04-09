import pymysql
from bd import Conexion_BD

def obtener_productos_inventario():
    productos = []
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            p.Id,
            p.nombre_producto,
            p.stock,
            p.stock_minimo,
            p.stock_maximo,
            COALESCE(t.tamano, 'No Aplica') as tamano
        FROM tproductos p
        LEFT JOIN tproductos_variantes pv ON p.Id = pv.producto_id
        LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
        INNER JOIN tcategorias c ON p.categoria_id = c.Id
        WHERE p.activo = 1
        AND (c.requiere_inventario = 1)
        ORDER BY p.nombre_producto
        """
        
        cursor.execute(query)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error al obtener productos para inventario: {e}")
    return productos

def obtener_productos_bajo_stock():
    """
    Obtiene los productos que están en nivel crítico o de alerta de stock
    """
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Consulta para obtener productos con stock bajo o crítico
        query = """
        SELECT p.Id, p.nombre_producto, p.stock, p.stock_minimo, p.stock_maximo,
            CASE 
                WHEN p.stock <= p.stock_minimo THEN 'critico'
                WHEN p.stock <= p.stock_minimo + 5 THEN 'critico'
                WHEN p.stock <= p.stock_minimo + 10 THEN 'alerta'
                ELSE 'normal'
            END as nivel_stock
        FROM tproductos p
        INNER JOIN tcategorias c ON p.categoria_id = c.Id
        WHERE (c.requiere_inventario = 1 OR c.categoria IN ('Postre', 'Snack'))
        AND (p.stock <= p.stock_minimo + 10)
        ORDER BY nivel_stock, p.nombre_producto
        """
        
        cursor.execute(query)
        productos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return productos
    except Exception as e:
        print(f"Error al obtener productos de bajo stock: {e}")
        return []

def actualizar_stock_producto(id_producto, nuevo_stock, nuevo_stock_min, nuevo_stock_max):
    """
    Actualiza el stock y los límites de stock de un producto
    """
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        query = """
        UPDATE tproductos 
        SET stock = %s, stock_minimo = %s, stock_maximo = %s
        WHERE Id = %s
        """
        
        cursor.execute(query, (nuevo_stock, nuevo_stock_min, nuevo_stock_max, id_producto))
        conn.commit()
        
        # Registrar el movimiento en la tabla de movimientos
        if cursor.rowcount > 0:
            # Obtener el stock anterior
            cursor.execute("SELECT stock FROM tproductos WHERE Id = %s", (id_producto,))
            stock_anterior = cursor.fetchone()['stock']
            
            # Determinar el tipo de movimiento (3 = Ajuste Positivo, 4 = Ajuste Negativo)
            tipo_movimiento = 3 if nuevo_stock >= stock_anterior else 4
            cantidad = abs(nuevo_stock - stock_anterior)
            
            if cantidad > 0:  # Solo registrar si hubo cambio en el stock
                query_movimiento = """
                INSERT INTO tmovimientosinventario (producto_id, cantidad, tipo_movimiento_id, motivo)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_movimiento, (id_producto, cantidad, tipo_movimiento, "Actualización desde panel de inventario"))
                conn.commit()
        
        resultado = cursor.rowcount > 0
        
        cursor.close()
        conn.close()
        
        return resultado
    except Exception as e:
        print(f"Error al actualizar stock: {e}")
        return False