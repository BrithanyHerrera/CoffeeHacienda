from bd import Conexion_BD
from datetime import datetime

def limpiar_validaciones_expiradas():
    """
    Elimina los registros de validación de usuarios que han expirado
    """
    try:
        conn = Conexion_BD()
        with conn.cursor() as cursor:
            # Eliminar registros expirados de la tabla de validación
            sql = "DELETE FROM tvalidacion_usuarios WHERE fecha_expiracion < %s"
            cursor.execute(sql, (datetime.now(),))
            registros_eliminados = cursor.rowcount
            conn.commit()
            
            print(f"Se eliminaron {registros_eliminados} registros de validación expirados")
            return registros_eliminados
    except Exception as e:
        print(f"Error al limpiar validaciones expiradas: {e}")
        return 0
    finally:
        conn.close()

def limpiar_codigos_recuperacion_expirados():
    """
    Elimina los códigos de recuperación de contraseña que han expirado
    """
    try:
        conn = Conexion_BD()
        with conn.cursor() as cursor:
            # Eliminar códigos de recuperación expirados
            sql = "DELETE FROM tcodigosrecuperacion WHERE fecha_expiracion < %s"
            cursor.execute(sql, (datetime.now(),))
            registros_eliminados = cursor.rowcount
            conn.commit()
            
            print(f"Se eliminaron {registros_eliminados} códigos de recuperación expirados")
            return registros_eliminados
    except Exception as e:
        print(f"Error al limpiar códigos de recuperación expirados: {e}")
        return 0
    finally:
        conn.close()