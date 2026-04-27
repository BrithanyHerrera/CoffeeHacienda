# Modelo de inventario — stock, alertas y movimientos
import logging
from bd import Conexion_BD

logger = logging.getLogger(__name__)


def obtener_producto_inventario_por_id(id_producto):
    """Obtiene stock y límites de un producto que requiere inventario."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.Id, p.stock, p.stock_minimo, p.stock_maximo
            FROM tproductos p
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.Id = %s AND p.activo = 1 AND c.requiere_inventario = 1
        """, (id_producto,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado
    finally:
        conn.close()


def obtener_productos_inventario():
    """Lista todos los productos activos que requieren control de inventario."""
    productos = []
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.Id, p.nombre_producto, p.stock, p.stock_minimo, p.stock_maximo,
                   COALESCE(t.tamano, 'No Aplica') as tamano
            FROM tproductos p
            LEFT JOIN tproductos_variantes pv ON p.Id = pv.producto_id
            LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.activo = 1 AND c.requiere_inventario = 1
            ORDER BY p.nombre_producto
        """)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error al obtener productos para inventario: {e}")
    return productos

def contar_alertas_inventario():
    """Cuenta alertas de stock directamente en MySQL. Retorna {criticas, normales}."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total FROM tproductos p
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.activo = 1 AND c.requiere_inventario = 1
            AND p.stock <= p.stock_minimo + 5
        """)
        criticas = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as total FROM tproductos p
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.activo = 1 AND c.requiere_inventario = 1
            AND p.stock > p.stock_minimo + 5
            AND p.stock <= p.stock_minimo + 10
        """)
        normales = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        return {'criticas': criticas, 'normales': normales}
    except Exception as e:
        logger.error(f"Error al contar alertas de inventario: {e}")
        return {'criticas': 0, 'normales': 0}

def obtener_productos_bajo_stock():
    """Obtiene productos en nivel crítico o de alerta."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("""
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
        """)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return productos
    except Exception as e:
        logger.error(f"Error al obtener productos de bajo stock: {e}")
        return []

def actualizar_stock_producto(id_producto, nuevo_stock, nuevo_stock_min, nuevo_stock_max):
    """Actualiza stock y límites; registra el movimiento en tmovimientosinventario."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Leer stock anterior para calcular el movimiento
        cursor.execute("SELECT stock FROM tproductos WHERE Id = %s", (id_producto,))
        fila = cursor.fetchone()
        stock_anterior = fila['stock'] if fila else 0
        
        cursor.execute("""
            UPDATE tproductos 
            SET stock = %s, stock_minimo = %s, stock_maximo = %s
            WHERE Id = %s
        """, (nuevo_stock, nuevo_stock_min, nuevo_stock_max, id_producto))
        conn.commit()
        
        if cursor.rowcount > 0:
            cantidad = abs(nuevo_stock - stock_anterior)
            tipo_movimiento = 3 if nuevo_stock >= stock_anterior else 4  # 3=Ajuste+, 4=Ajuste-
            
            if cantidad > 0:
                try:
                    # tmovimientosinventario no tiene AUTO_INCREMENT
                    cursor.execute("SELECT COALESCE(MAX(Id), 0) + 1 AS next_id FROM tmovimientosinventario")
                    next_id = cursor.fetchone()['next_id']
                    
                    cursor.execute("""
                        INSERT INTO tmovimientosinventario (Id, producto_id, cantidad, tipo_movimiento_id, motivo)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (next_id, id_producto, cantidad, tipo_movimiento, "Actualización desde panel de inventario"))
                    conn.commit()
                except Exception as mov_error:
                    logger.warning(f"No se registró movimiento de inventario: {mov_error}")
        
        resultado = cursor.rowcount > 0
        cursor.close()
        conn.close()
        return resultado
    except Exception as e:
        logger.error(f"Error al actualizar stock: {e}")
        return False