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

def contar_alertas_inventario():
    """
    Cuenta las alertas de inventario directamente en MySQL (sin traer toda la tabla).
    Retorna un diccionario con 'criticas' y 'normales'.
    """
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Contar alertas críticas (stock <= stock_minimo + 5)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM tproductos p
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.activo = 1
            AND c.requiere_inventario = 1
            AND p.stock <= p.stock_minimo + 5
        """)
        criticas = cursor.fetchone()['total']
        
        # Contar alertas normales (stock entre stock_minimo + 5 y stock_minimo + 10)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM tproductos p
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.activo = 1
            AND c.requiere_inventario = 1
            AND p.stock > p.stock_minimo + 5
            AND p.stock <= p.stock_minimo + 10
        """)
        normales = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return {'criticas': criticas, 'normales': normales}
    except Exception as e:
        print(f"Error al contar alertas de inventario: {e}")
        return {'criticas': 0, 'normales': 0}

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
        # Validar que los valores no sean cero
        if nuevo_stock_min == 0 or nuevo_stock_max == 0:
            print("Error: Los valores de stock mínimo y máximo no pueden ser cero")
            return False
            
        # Validar que el stock mínimo y máximo no sean iguales
        if nuevo_stock_min == nuevo_stock_max:
            print("Error: El stock mínimo y máximo no pueden ser iguales")
            return False
            
        # Validar que el stock mínimo no sea mayor que el stock máximo
        if nuevo_stock_min > nuevo_stock_max:
            print(f"Error: El stock mínimo ({nuevo_stock_min}) no puede ser mayor que el stock máximo ({nuevo_stock_max})")
            return False
            
        # Validar que el stock máximo no sea menor que el stock mínimo
        if nuevo_stock_max < nuevo_stock_min:
            print(f"Error: El stock máximo ({nuevo_stock_max}) no puede ser menor que el stock mínimo ({nuevo_stock_min})")
            return False
            
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Leer el stock anterior ANTES del UPDATE
        cursor.execute("SELECT stock FROM tproductos WHERE Id = %s", (id_producto,))
        fila_anterior = cursor.fetchone()
        stock_anterior = fila_anterior['stock'] if fila_anterior else 0
        
        query = """
        UPDATE tproductos 
        SET stock = %s, stock_minimo = %s, stock_maximo = %s
        WHERE Id = %s
        """
        
        cursor.execute(query, (nuevo_stock, nuevo_stock_min, nuevo_stock_max, id_producto))
        conn.commit()
        
        # Registrar el movimiento en la tabla de movimientos
        if cursor.rowcount > 0:
            # Determinar el tipo de movimiento (3 = Ajuste Positivo, 4 = Ajuste Negativo)
            cantidad = abs(nuevo_stock - stock_anterior)
            tipo_movimiento = 3 if nuevo_stock >= stock_anterior else 4
            
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