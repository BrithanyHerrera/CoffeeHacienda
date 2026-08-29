# Menú: productos activos con variantes de tamaño
import logging
from bd import Conexion_BD
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


def obtener_metodos_pago():
    """Devuelve el catálogo de pagos con una clave estable para la interfaz."""
    conn = Conexion_BD()
    try:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT Id AS id, codigo, tipo_de_pago AS nombre
                FROM tmetodospago
                ORDER BY FIELD(codigo, 'EFECTIVO', 'TARJETA', 'TRANSFERENCIA'), Id
            """)
            return cursor.fetchall()
    except Exception as error:
        logger.error("Error al obtener métodos de pago: %s", error)
        return []
    finally:
        conn.close()

def obtener_productos_menu():
    productos = []
    conn = None
    
    try:
        conn = Conexion_BD()
        if not conn:
            logger.warning("No se pudo conectar a la base de datos")
            return productos
        
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT p.id, p.nombre_producto, p.descripcion, p.precio, p.stock,
                       p.stock_minimo, p.stock_maximo, p.categoria_id, p.ruta_imagen, 
                       c.categoria, c.requiere_inventario
                FROM tproductos p 
                LEFT JOIN tcategorias c ON p.categoria_id = c.id
                WHERE p.activo = 1
                ORDER BY p.nombre_producto
            """)
            productos = cursor.fetchall()
            
            if productos:
                # Traer todas las variantes en una sola consulta (evita N+1)
                producto_ids = [p['id'] for p in productos]
                placeholders = ', '.join(['%s'] * len(producto_ids))
                cursor.execute(f"""
                    SELECT pv.Id AS variante_id, pv.producto_id, t.tamano, pv.precio
                    FROM tproductos_variantes pv
                    JOIN ttamanos t ON pv.tamano_id = t.id
                    WHERE pv.producto_id IN ({placeholders})
                    ORDER BY pv.producto_id, pv.Id
                """, producto_ids)
                
                variantes_por_producto = {}
                for v in cursor.fetchall():
                    pid = v['producto_id']
                    if pid not in variantes_por_producto:
                        variantes_por_producto[pid] = []
                    variantes_por_producto[pid].append({
                        'variante_id': v['variante_id'],
                        'tamano': v['tamano'],
                        'precio': v['precio']
                    })
                
                for producto in productos:
                    producto["variantes"] = variantes_por_producto.get(producto["id"], [])

    except Exception as e:
        logger.error(f"Error al obtener productos: {e}")
    finally:
        if conn is not None:
            conn.close()
    
    return productos
