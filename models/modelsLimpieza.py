# Limpieza: borra registros temporales expirados al iniciar
import logging
from bd import Conexion_BD
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def limpiar_validaciones_expiradas():
    """Elimina validaciones de usuarios que llevan más de 30 minutos sin completarse."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM tvalidacion_usuarios
                WHERE validado = FALSE AND fecha_creacion < %s
            """, (datetime.now() - timedelta(minutes=30),))
            registros = cursor.rowcount
        conn.commit()
        return registros
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al limpiar validaciones expiradas: {e}")
        return 0
    finally:
        conn.close()

def limpiar_codigos_recuperacion_expirados():
    """Elimina códigos de recuperación de contraseña que ya expiraron."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tcodigosrecuperacion WHERE fecha_expiracion < %s", (datetime.now(),))
            registros = cursor.rowcount
        conn.commit()
        return registros
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al limpiar códigos expirados: {e}")
        return 0
    finally:
        conn.close()