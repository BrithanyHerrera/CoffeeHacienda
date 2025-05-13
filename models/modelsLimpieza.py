from bd import Conexion_BD
from datetime import datetime, timedelta

def limpiar_validaciones_expiradas():
    """Elimina las validaciones de usuarios que han expirado (más de 30 minutos)"""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Eliminar registros expirados (más de 30 minutos)
        sql = """
            DELETE FROM tvalidacion_usuarios
            WHERE validado = FALSE AND fecha_creacion < %s
        """
        cursor.execute(sql, (datetime.now() - timedelta(minutes=30),))
        
        registros_eliminados = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return registros_eliminados
    except Exception as e:
        print(f"Error al limpiar validaciones expiradas: {e}")
        return 0

def limpiar_codigos_recuperacion_expirados():
    """Elimina los códigos de recuperación que han expirado"""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Eliminar códigos expirados
        sql = """
            DELETE FROM tcodigosrecuperacion
            WHERE fecha_expiracion < %s
        """
        cursor.execute(sql, (datetime.now(),))
        
        registros_eliminados = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return registros_eliminados
    except Exception as e:
        print(f"Error al limpiar códigos de recuperación expirados: {e}")
        return 0