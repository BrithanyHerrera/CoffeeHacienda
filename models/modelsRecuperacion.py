# Recuperación de contraseña: códigos por correo
import logging
import secrets
import string
from datetime import datetime

from bd import Conexion_BD

logger = logging.getLogger(__name__)

def generar_codigo(longitud=6):
    """Genera un código numérico criptográficamente seguro."""
    if not isinstance(longitud, int) or not 4 <= longitud <= 10:
        raise ValueError("La longitud del código debe estar entre 4 y 10 dígitos")
    return ''.join(secrets.choice(string.digits) for _ in range(longitud))

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
        conn.rollback()
        logger.error(f"Error al guardar código de recuperación: {e}")
        return False
    finally:
        conn.close()

def verificar_codigo_recuperacion(usuario_id, codigo, consumir=False,
                                  codigo_consumido=None, expiracion_consumido=None):
    """Verifica un código vigente y, opcionalmente, lo consume de forma atómica.

    Al consumirlo, el bloqueo de fila garantiza que dos solicitudes concurrentes
    no puedan obtener autorización con el mismo código.
    """
    codigo = str(codigo or '').strip()
    if not codigo or len(codigo) > 10 or not codigo.isdigit():
        return False

    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Id, codigo
                FROM tcodigosrecuperacion
                WHERE usuario_id = %s AND fecha_expiracion > %s
                ORDER BY fecha_creacion DESC, Id DESC
                LIMIT 1
                FOR UPDATE
            """, (usuario_id, datetime.now()))
            registro = cursor.fetchone()

            if not registro or not secrets.compare_digest(str(registro['codigo']), codigo):
                conn.rollback()
                return False

            if consumir:
                codigo_consumido = str(codigo_consumido or '')
                if (not codigo_consumido or len(codigo_consumido) > 10
                        or expiracion_consumido is None):
                    conn.rollback()
                    return False

                cursor.execute(
                    """
                    UPDATE tcodigosrecuperacion
                    SET codigo = %s, fecha_expiracion = %s
                    WHERE Id = %s
                    """,
                    (codigo_consumido, expiracion_consumido, registro['Id']),
                )
                if cursor.rowcount != 1:
                    conn.rollback()
                    return False
                conn.commit()
            else:
                # Libera inmediatamente el bloqueo adquirido con FOR UPDATE.
                conn.rollback()

            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al verificar código: {e}")
        return False
    finally:
        conn.close()

def eliminar_codigos_recuperacion(usuario_id):
    """Invalida cualquier código pendiente de un usuario."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tcodigosrecuperacion WHERE usuario_id = %s",
                (usuario_id,),
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al eliminar códigos de recuperación: {e}")
        return False
    finally:
        conn.close()

def actualizar_contrasena_por_codigo(usuario_id, nueva_contrasena, codigo_consumido):
    """Consume el permiso de recuperación y actualiza la clave atómicamente."""
    codigo_consumido = str(codigo_consumido or '')
    if not codigo_consumido or len(codigo_consumido) > 10:
        return False

    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Id, codigo
                FROM tcodigosrecuperacion
                WHERE usuario_id = %s AND fecha_expiracion > %s
                ORDER BY fecha_creacion DESC, Id DESC
                LIMIT 1
                FOR UPDATE
            """, (usuario_id, datetime.now()))
            registro = cursor.fetchone()
            if (not registro
                    or not secrets.compare_digest(str(registro['codigo']), codigo_consumido)):
                conn.rollback()
                return False

            cursor.execute("""
                UPDATE tusuarios
                SET contrasena = %s, sesion_version = sesion_version + 1
                WHERE Id = %s
            """, (nueva_contrasena, usuario_id))
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            cursor.execute(
                "DELETE FROM tcodigosrecuperacion WHERE Id = %s",
                (registro['Id'],),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al actualizar contraseña: {e}")
        return False
    finally:
        conn.close()
