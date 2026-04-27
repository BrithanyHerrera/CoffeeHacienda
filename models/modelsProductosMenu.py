# Modelo del menú — consulta de productos activos con sus variantes de tamaño
import logging
from bd import Conexion_BD
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)

def obtener_productos_menu():
    productos = []
    
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
                    SELECT pv.producto_id, t.tamano, pv.precio 
                    FROM tproductos_variantes pv
                    JOIN ttamanos t ON pv.tamano_id = t.id
                    WHERE pv.producto_id IN ({placeholders})
                """, producto_ids)
                
                variantes_por_producto = {}
                for v in cursor.fetchall():
                    pid = v['producto_id']
                    if pid not in variantes_por_producto:
                        variantes_por_producto[pid] = []
                    variantes_por_producto[pid].append({'tamano': v['tamano'], 'precio': v['precio']})
                
                for producto in productos:
                    producto["variantes"] = variantes_por_producto.get(producto["id"], [])

        conn.close()
        
    except Exception as e:
        logger.error(f"Error al obtener productos: {e}")
    
    return productos
