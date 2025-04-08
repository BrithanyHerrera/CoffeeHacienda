from bd import Conexion_BD
from datetime import datetime
import random
import string

def generar_codigo_recuperacion(longitud=6):
    """
    Genera un código aleatorio de la longitud especificada
    """
    return ''.join(random.choices(string.digits, k=longitud))

def guardar_codigo_recuperacion(usuario_id, codigo, expiracion):
    """
    Guarda un código de recuperación para un usuario
    """
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            # Primero eliminar códigos anteriores del mismo usuario
            sql_delete = "DELETE FROM tcodigosrecuperacion WHERE usuario_id = %s"
            cursor.execute(sql_delete, (usuario_id,))
            
            # Insertar el nuevo código
            sql_insert = """
            INSERT INTO tcodigosrecuperacion (usuario_id, codigo, fecha_expiracion)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql_insert, (usuario_id, codigo, expiracion))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al guardar código de recuperación: {e}")
        return False
    finally:
        conn.close()

def verificar_codigo_recuperacion(usuario_id, codigo):
    """
    Verifica si un código de recuperación es válido y no ha expirado
    """
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT * FROM tcodigosrecuperacion 
            WHERE usuario_id = %s AND codigo = %s AND fecha_expiracion > %s
            """
            cursor.execute(sql, (usuario_id, codigo, datetime.now()))
            resultado = cursor.fetchone()
            return resultado is not None
    except Exception as e:
        print(f"Error al verificar código: {e}")
        return False
    finally:
        conn.close()

def actualizar_contrasena_por_codigo(usuario_id, nueva_contrasena):
    """
    Actualiza la contraseña de un usuario y elimina el código de recuperación
    """
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            # Actualizar contraseña
            sql_update = "UPDATE tusuarios SET contrasena = %s WHERE Id = %s"
            cursor.execute(sql_update, (nueva_contrasena, usuario_id))
            
            # Eliminar código de recuperación
            sql_delete = "DELETE FROM tcodigosrecuperacion WHERE usuario_id = %s"
            cursor.execute(sql_delete, (usuario_id,))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al actualizar contraseña: {e}")
        return False
    finally:
        conn.close()