# Modelo de recuperación de contraseña — códigos de verificación por correo
import logging
from bd import Conexion_BD
from datetime import datetime
import random
import string

logger = logging.getLogger(__name__)

def generar_codigo(longitud=6):
    """Genera un código numérico aleatorio."""
    return ''.join(random.choices(string.digits, k=longitud))

def guardar_codigo_recuperacion(usuario_id, codigo, expiracion):
    """Guarda un código nuevo y elimina los anteriores del usuario."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tcodigosrecuperacion WHERE usuario_id = %s", (usuario_id,))
            cursor.execute("""
                INSERT INTO tcodigosrecuperacion (usuario_id, codigo, fecha_expiracion)
                VALUES (%s, %s, %s)
            """, (usuario_id, codigo, expiracion))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error al guardar código de recuperación: {e}")
        return False
    finally:
        conn.close()

def verificar_codigo_recuperacion(usuario_id, codigo):
    """Verifica que el código sea válido y no haya expirado."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM tcodigosrecuperacion 
                WHERE usuario_id = %s AND codigo = %s AND fecha_expiracion > %s
            """, (usuario_id, codigo, datetime.now()))
            return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error al verificar código: {e}")
        return False
    finally:
        conn.close()

def actualizar_contrasena_por_codigo(usuario_id, nueva_contrasena):
    """Actualiza la contraseña y limpia el código de recuperación usado."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE tusuarios SET contrasena = %s WHERE Id = %s", (nueva_contrasena, usuario_id))
            cursor.execute("DELETE FROM tcodigosrecuperacion WHERE usuario_id = %s", (usuario_id,))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error al actualizar contraseña: {e}")
        return False
    finally:
        conn.close()