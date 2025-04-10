from bd import Conexion_BD
import os
from datetime import datetime
import pymysql

def obtener_productos():
    productos = []
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, c.categoria 
                FROM tproductos p 
                JOIN tcategorias c ON p.categoria_id = c.id 
                WHERE p.activo = 1
                ORDER BY p.Id DESC
            """)
            productos = cursor.fetchall()
        connection.close()
    except Exception as e:
        print(f"Error al obtener productos: {e}")
    return productos

def obtener_categorias():
    categorias = []
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = "SELECT * FROM tcategorias ORDER BY categoria"
            cursor.execute(query)
            categorias = cursor.fetchall()
        connection.close()
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
    
    return categorias

def obtener_tamanos():
    tamanos = []
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = "SELECT * FROM ttamanos ORDER BY Id"
            cursor.execute(query)
            tamanos = cursor.fetchall()
        connection.close()
    except Exception as e:
        print(f"Error al obtener tamaños: {e}")
    
    return tamanos

def agregar_variante_producto(producto_id, tamano_id, precio):
    resultado = False
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = """
            INSERT INTO tproductos_variantes (producto_id, tamano_id, precio)
            VALUES (%s, %s, %s)
            """
            valores = (producto_id, tamano_id, precio)
            cursor.execute(query, valores)
        connection.commit()
        resultado = True
        connection.close()
    except Exception as e:
        print(f"Error al agregar variante de producto: {e}")
    
    return resultado

def obtener_variantes_por_producto(producto_id):
    variantes = []
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = """
            SELECT pv.*, t.tamano 
            FROM tproductos_variantes pv 
            JOIN ttamanos t ON pv.tamano_id = t.Id
            WHERE pv.producto_id = %s
            ORDER BY t.Id
            """
            cursor.execute(query, (producto_id,))
            variantes = cursor.fetchall()
        connection.close()
    except Exception as e:
        print(f"Error al obtener variantes del producto: {e}")
    
    return variantes

def actualizar_variante_producto(variante_id, precio):
    resultado = False
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = """
            UPDATE tproductos_variantes 
            SET precio = %s
            WHERE Id = %s
            """
            valores = (precio, variante_id)
            cursor.execute(query, valores)
        connection.commit()
        resultado = cursor.rowcount > 0
        connection.close()
    except Exception as e:
        print(f"Error al actualizar variante de producto: {e}")
    
    return resultado

def eliminar_variantes_producto(producto_id):
    resultado = False
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = "DELETE FROM tproductos_variantes WHERE producto_id = %s"
            cursor.execute(query, (producto_id,))
        connection.commit()
        resultado = True
        connection.close()
    except Exception as e:
        print(f"Error al eliminar variantes del producto: {e}")
    
    return resultado

def agregar_producto(nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen):
    resultado = False
    producto_id = None
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = """
            INSERT INTO tproductos (nombre_producto, descripcion, precio, stock, 
                                stock_minimo, stock_maximo, categoria_id, ruta_imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen)
            cursor.execute(query, valores)
            # Obtenemos el ID del producto recién insertado
            producto_id = cursor.lastrowid
        connection.commit()
        resultado = True
        connection.close()
    except Exception as e:
        print(f"Error al agregar producto: {e}")
    
    return resultado, producto_id  # Devolvemos tanto el resultado como el ID

def actualizar_producto(id, nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen=None):
    resultado = False
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            # Si se proporciona una nueva imagen, actualizar también la ruta de la imagen
            if ruta_imagen:
                query = """
                UPDATE tproductos 
                SET nombre_producto = %s, descripcion = %s, precio = %s, stock = %s,
                    stock_minimo = %s, stock_maximo = %s, categoria_id = %s, ruta_imagen = %s
                WHERE Id = %s
                """
                valores = (nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen, id)
            else:
                # Si no se proporciona una nueva imagen, mantener la imagen actual
                query = """
                UPDATE tproductos 
                SET nombre_producto = %s, descripcion = %s, precio = %s, stock = %s,
                    stock_minimo = %s, stock_maximo = %s, categoria_id = %s
                WHERE Id = %s
                """
                valores = (nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, id)
                
            cursor.execute(query, valores)
        connection.commit()
        resultado = cursor.rowcount > 0
        connection.close()
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
    
    return resultado

def eliminar_producto(id_producto):
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # En lugar de DELETE, hacemos un UPDATE para marcar como inactivo
        cursor.execute("""
            UPDATE tproductos 
            SET activo = 0 
            WHERE Id = %s
        """, (id_producto,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al marcar producto como eliminado: {str(e)}")
        return False
    
    resultado = False
    
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = "DELETE FROM tproductos WHERE Id = %s"
            cursor.execute(query, (id,))
        connection.commit()
        resultado = cursor.rowcount > 0
        connection.close()
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
    
    return resultado

def obtener_producto_por_id(id):
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.*,
                    c.categoria
                FROM tproductos p 
                JOIN tcategorias c ON p.categoria_id = c.id 
                WHERE p.Id = %s AND p.activo = 1
            """, (id,))
            producto = cursor.fetchone()
            
            if producto:
                # Obtener las variantes por separado
                cursor.execute("""
                    SELECT 
                        pv.Id,
                        pv.producto_id,
                        pv.tamano_id,
                        pv.precio,
                        t.tamano
                    FROM tproductos_variantes pv
                    JOIN ttamanos t ON pv.tamano_id = t.Id
                    WHERE pv.producto_id = %s
                """, (id,))
                producto['variantes'] = cursor.fetchall()
            
            return producto
    except Exception as e:
        print(f"Error al obtener producto por ID: {e}")