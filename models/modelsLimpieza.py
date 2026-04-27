# Modelo de limpieza — elimina registros temporales expirados al arrancar
import logging
from bd import Conexion_BD
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def limpiar_validaciones_expiradas():
    """Elimina validaciones de usuarios que llevan más de 30 minutos sin completarse."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM tvalidacion_usuarios
            WHERE validado = FALSE AND fecha_creacion < %s
        """, (datetime.now() - timedelta(minutes=30),))
        registros = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return registros
    except Exception as e:
        logger.error(f"Error al limpiar validaciones expiradas: {e}")
        return 0

def limpiar_codigos_recuperacion_expirados():
    """Elimina códigos de recuperación de contraseña que ya expiraron."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tcodigosrecuperacion WHERE fecha_expiracion < %s", (datetime.now(),))
        registros = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return registros
    except Exception as e:
        logger.error(f"Error al limpiar códigos expirados: {e}")
        return 0