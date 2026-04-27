# Modelo de productos — CRUD, variantes y categorías
import logging
from bd import Conexion_BD

logger = logging.getLogger(__name__)


def obtener_variantes_batch(producto_ids):
    """Trae todas las variantes para una lista de IDs en una sola consulta."""
    if not producto_ids:
        return {}
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(producto_ids))
            cursor.execute(f"""
                SELECT pv.*, t.tamano 
                FROM tproductos_variantes pv 
                JOIN ttamanos t ON pv.tamano_id = t.Id
                WHERE pv.producto_id IN ({placeholders})
                ORDER BY t.Id
            """, producto_ids)
            todas = cursor.fetchall()
        resultado = {}
        for v in todas:
            pid = v['producto_id']
            if pid not in resultado:
                resultado[pid] = []
            resultado[pid].append(v)
        return resultado
    finally:
        conn.close()


def obtener_productos():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, c.categoria 
                FROM tproductos p 
                JOIN tcategorias c ON p.categoria_id = c.id 
                WHERE p.activo = 1 ORDER BY p.Id DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener productos: {e}")
        return []
    finally:
        conn.close()

def obtener_categorias():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tcategorias ORDER BY categoria")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener categorías: {e}")
        return []
    finally:
        conn.close()

def obtener_tamanos():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ttamanos ORDER BY Id")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener tamaños: {e}")
        return []
    finally:
        conn.close()

def agregar_variante_producto(producto_id, tamano_id, precio):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tproductos_variantes (producto_id, tamano_id, precio)
                VALUES (%s, %s, %s)
            """, (producto_id, tamano_id, precio))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error al agregar variante: {e}")
        return False
    finally:
        conn.close()

def obtener_variantes_por_producto(producto_id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT pv.*, t.tamano 
                FROM tproductos_variantes pv 
                JOIN ttamanos t ON pv.tamano_id = t.Id
                WHERE pv.producto_id = %s ORDER BY t.Id
            """, (producto_id,))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener variantes: {e}")
        return []
    finally:
        conn.close()

def actualizar_variante_producto(variante_id, precio):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE tproductos_variantes SET precio = %s WHERE Id = %s", (precio, variante_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error al actualizar variante: {e}")
        return False
    finally:
        conn.close()

def eliminar_variantes_producto(producto_id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tproductos_variantes WHERE producto_id = %s", (producto_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error al eliminar variantes: {e}")
        return False
    finally:
        conn.close()

def agregar_producto(nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tproductos (nombre_producto, descripcion, precio, stock, 
                                    stock_minimo, stock_maximo, categoria_id, ruta_imagen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen))
            producto_id = cursor.lastrowid
        conn.commit()
        return True, producto_id
    except Exception as e:
        logger.error(f"Error al agregar producto: {e}")
        return False, None
    finally:
        conn.close()

def actualizar_producto(id, nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen=None):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            if ruta_imagen:
                cursor.execute("""
                    UPDATE tproductos 
                    SET nombre_producto=%s, descripcion=%s, precio=%s, stock=%s,
                        stock_minimo=%s, stock_maximo=%s, categoria_id=%s, ruta_imagen=%s
                    WHERE Id=%s
                """, (nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen, id))
            else:
                cursor.execute("""
                    UPDATE tproductos 
                    SET nombre_producto=%s, descripcion=%s, precio=%s, stock=%s,
                        stock_minimo=%s, stock_maximo=%s, categoria_id=%s
                    WHERE Id=%s
                """, (nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, id))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Producto actualizado correctamente"
        return False, "No se realizaron cambios en el producto"
    except Exception as e:
        logger.error(f"Error al actualizar producto: {e}")
        return False, f"Error al actualizar producto: {e}"
    finally:
        conn.close()

def eliminar_producto(id_producto):
    """Soft-delete: marca el producto como inactivo."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tproductos SET activo = 0 WHERE Id = %s", (id_producto,))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Error al desactivar producto: {str(e)}")
        return False
    finally:
        conn.close()

def obtener_producto_por_id(id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, c.categoria
                FROM tproductos p 
                JOIN tcategorias c ON p.categoria_id = c.id 
                WHERE p.Id = %s AND p.activo = 1
            """, (id,))
            producto = cursor.fetchone()
            if producto:
                cursor.execute("""
                    SELECT pv.Id, pv.producto_id, pv.tamano_id, pv.precio, t.tamano
                    FROM tproductos_variantes pv
                    JOIN ttamanos t ON pv.tamano_id = t.Id
                    WHERE pv.producto_id = %s
                """, (id,))
                producto['variantes'] = cursor.fetchall()
            return producto
    except Exception as e:
        logger.error(f"Error al obtener producto por ID: {e}")
        return None
    finally:
        conn.close()