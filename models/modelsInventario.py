# Inventario: stock, alertas y movimientos
import logging
from bd import Conexion_BD

logger = logging.getLogger(__name__)


def obtener_producto_inventario_por_id(id_producto):
    """Obtiene stock y límites de un producto que requiere inventario."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.Id, p.stock, p.stock_minimo, p.stock_maximo
                FROM tproductos p
                INNER JOIN tcategorias c ON p.categoria_id = c.Id
                WHERE p.Id = %s AND p.activo = 1 AND c.requiere_inventario = 1
            """, (id_producto,))
            return cursor.fetchone()
    finally:
        conn.close()


def obtener_productos_inventario():
    """Lista todos los productos activos que requieren control de inventario."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
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
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener productos para inventario: {e}")
        return []
    finally:
        conn.close()

def contar_alertas_inventario():
    """Cuenta alertas de stock directamente en MySQL. Retorna {criticas, normales}."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
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
            
            return {'criticas': criticas, 'normales': normales}
    except Exception as e:
        logger.error(f"Error al contar alertas de inventario: {e}")
        return {'criticas': 0, 'normales': 0}
    finally:
        conn.close()

def actualizar_stock_producto(id_producto, nuevo_stock, nuevo_stock_min, nuevo_stock_max):
    """Actualiza stock y límites; registra el movimiento en tmovimientosinventario."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            # Bloquear la fila para que el ajuste y su movimiento sean atómicos.
            cursor.execute("SELECT stock FROM tproductos WHERE Id = %s FOR UPDATE", (id_producto,))
            fila = cursor.fetchone()
            if not fila:
                conn.rollback()
                return False

            stock_anterior = fila['stock']
            
            cursor.execute("""
                UPDATE tproductos 
                SET stock = %s, stock_minimo = %s, stock_maximo = %s
                WHERE Id = %s
            """, (nuevo_stock, nuevo_stock_min, nuevo_stock_max, id_producto))

            cantidad = abs(nuevo_stock - stock_anterior)
            tipo_movimiento = 3 if nuevo_stock >= stock_anterior else 4  # 3=Ajuste+, 4=Ajuste-

            if cantidad > 0:
                cursor.execute("""
                    INSERT INTO tmovimientosinventario (producto_id, cantidad, tipo_movimiento_id, motivo)
                    VALUES (%s, %s, %s, %s)
                """, (id_producto, cantidad, tipo_movimiento, "Actualización desde panel de inventario"))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al actualizar stock: {e}")
        return False
    finally:
        conn.close()
