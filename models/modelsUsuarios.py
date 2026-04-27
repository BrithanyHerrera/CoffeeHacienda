# Modelo de usuarios — CRUD, validación por código y gestión de activos/inactivos
import logging
from datetime import datetime, timedelta
from bd import Conexion_BD
from models.modelsRecuperacion import generar_codigo

logger = logging.getLogger(__name__)

def verificar_usuario_existente(usuario):
    """Verifica si un nombre de usuario ya está en uso (entre activos)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM tusuarios WHERE usuario = %s AND activo = 1", (usuario,))
            return cursor.fetchone()['count'] > 0
    except Exception as e:
        logger.error(f"Error al verificar usuario: {e}")
        return False
    finally:
        conn.close()

def verificar_correo_existente(correo):
    """Verifica si un correo ya está registrado (entre activos)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM tusuarios WHERE correo = %s AND activo = 1", (correo,))
            return cursor.fetchone()['count'] > 0
    except Exception as e:
        logger.error(f"Error al verificar correo: {e}")
        return False
    finally:
        conn.close()

def crear_usuario(usuario, contrasena, correo, rol_id):
    if verificar_usuario_existente(usuario):
        return False, "El nombre de usuario ya está en uso"
    if verificar_correo_existente(correo):
        return False, "El correo electrónico ya está registrado"
    
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO tusuarios (usuario, contrasena, rol_id, correo) VALUES (%s, %s, %s, %s)",
                          (usuario, contrasena, rol_id, correo))
        conn.commit()
        return True, "Usuario creado exitosamente"
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al crear usuario: {e}")
        return False, f"Error al crear usuario: {str(e)}"
    finally:
        conn.close()

def obtener_usuarios():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.Id, u.usuario, u.contrasena, u.correo, r.rol, r.Id as rol_id, u.creado_en 
                FROM tusuarios u JOIN troles r ON u.rol_id = r.Id
                WHERE u.activo = 1
            """)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        return []
    finally:
        conn.close()

def actualizar_usuario(id, usuario, contrasena, correo, rol_id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            # Verificar unicidad de nombre (excluyendo al mismo usuario)
            cursor.execute("SELECT COUNT(*) as count FROM tusuarios WHERE usuario = %s AND Id != %s", (usuario, id))
            if cursor.fetchone()['count'] > 0:
                return False, "El nombre de usuario ya está en uso por otro usuario"
            
            # Verificar unicidad de correo
            cursor.execute("SELECT COUNT(*) as count FROM tusuarios WHERE correo = %s AND Id != %s", (correo, id))
            if cursor.fetchone()['count'] > 0:
                return False, "El correo electrónico ya está registrado por otro usuario"
            
            cursor.execute("UPDATE tusuarios SET usuario=%s, contrasena=%s, rol_id=%s, correo=%s WHERE Id=%s",
                          (usuario, contrasena, rol_id, correo, id))
        conn.commit()
        return True, "Usuario actualizado exitosamente"
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al actualizar usuario: {e}")
        return False, f"Error al actualizar usuario: {str(e)}"
    finally:
        conn.close()

def obtener_usuario_por_id(id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT u.*, r.rol FROM tusuarios u JOIN troles r ON u.rol_id = r.Id WHERE u.Id = %s", (id,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener usuario por ID: {e}")
        return None
    finally:
        conn.close()

def obtener_roles():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM troles")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener roles: {e}")
        return []
    finally:
        conn.close()

def obtener_usuario_por_correo(correo):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT u.*, r.rol FROM tusuarios u JOIN troles r ON u.rol_id = r.Id WHERE u.correo = %s", (correo,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener usuario por correo: {e}")
        return None
    finally:
        conn.close()

def guardar_usuario_pendiente(usuario, contrasena, correo, rol_id):
    """Guarda un usuario en tabla temporal, genera código de validación."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Id FROM tusuarios WHERE correo = %s", (correo,))
        if cursor.fetchone():
            cursor.close(); conn.close()
            return False, "Ya existe un usuario con ese correo electrónico", None
        
        cursor.execute("SELECT id FROM tvalidacion_usuarios WHERE correo = %s AND validado = FALSE", (correo,))
        if cursor.fetchone():
            cursor.close(); conn.close()
            return False, "Ya existe una solicitud pendiente para este correo", None
        
        codigo = generar_codigo()
        cursor.execute("""
            INSERT INTO tvalidacion_usuarios (usuario, contrasena, correo, rol_id, codigo, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario, contrasena, correo, rol_id, codigo, datetime.now()))
        
        conn.commit()
        id_validacion = cursor.lastrowid
        cursor.close(); conn.close()
        return True, "Usuario pendiente de validación", {"id": id_validacion, "codigo": codigo}
    except Exception as e:
        logger.error(f"Error al guardar usuario pendiente: {e}")
        return False, f"Error: {str(e)}", None

def validar_codigo_usuario(correo, codigo):
    """Valida el código y crea el usuario definitivo en tusuarios."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, usuario, contrasena, correo, rol_id, fecha_creacion
            FROM tvalidacion_usuarios
            WHERE correo = %s AND codigo = %s AND validado = FALSE
        """, (correo, codigo))
        validacion = cursor.fetchone()
        
        if not validacion:
            cursor.close(); conn.close()
            return False, "Código de validación incorrecto o expirado"
        
        # Expira a los 30 min
        if datetime.now() - validacion['fecha_creacion'] > timedelta(minutes=30):
            cursor.close(); conn.close()
            return False, "El código de validación ha expirado"
        
        cursor.execute("INSERT INTO tusuarios (usuario, contrasena, correo, rol_id) VALUES (%s, %s, %s, %s)",
                       (validacion['usuario'], validacion['contrasena'], validacion['correo'], validacion['rol_id']))
        cursor.execute("DELETE FROM tvalidacion_usuarios WHERE id = %s", (validacion['id'],))
        
        conn.commit()
        cursor.close(); conn.close()
        return True, "Usuario validado correctamente"
    except Exception as e:
        logger.error(f"Error al validar código: {e}")
        return False, f"Error: {str(e)}"

def reenviar_codigo_validacion(correo):
    """Genera un código nuevo para una solicitud pendiente."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM tvalidacion_usuarios WHERE correo = %s AND validado = FALSE", (correo,))
        validacion = cursor.fetchone()
        
        if not validacion:
            cursor.close(); conn.close()
            return False, "No se encontró una solicitud pendiente para este correo", None
        
        nuevo_codigo = generar_codigo()
        cursor.execute("UPDATE tvalidacion_usuarios SET codigo = %s, fecha_creacion = %s WHERE id = %s",
                       (nuevo_codigo, datetime.now(), validacion['id']))
        
        conn.commit()
        cursor.close(); conn.close()
        return True, "Código regenerado correctamente", nuevo_codigo
    except Exception as e:
        logger.error(f"Error al reenviar código: {e}")
        return False, f"Error: {str(e)}", None

def reactivar_usuario(id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE tusuarios SET activo = 1, modificado_en = NOW() WHERE Id = %s", (id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al reactivar usuario: {e}")
        return False
    finally:
        conn.close()

def obtener_usuarios_activos():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.Id, u.usuario, u.correo, r.rol, r.Id as rol_id, u.creado_en 
                FROM tusuarios u JOIN troles r ON u.rol_id = r.Id
                WHERE u.activo = 1 ORDER BY u.usuario
            """)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener usuarios activos: {e}")
        return []
    finally:
        conn.close()

def obtener_usuarios_inactivos():
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.Id, u.usuario, u.correo, r.rol, r.Id as rol_id, u.creado_en, u.modificado_en
                FROM tusuarios u JOIN troles r ON u.rol_id = r.Id
                WHERE u.activo = 0 ORDER BY u.modificado_en DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener usuarios inactivos: {e}")
        return []
    finally:
        conn.close()

def desactivar_usuario(id):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Id FROM tusuarios WHERE Id = %s", (id,))
            if not cursor.fetchone():
                return False, 'Usuario no encontrado'
            cursor.execute("UPDATE tusuarios SET activo = 0 WHERE Id = %s", (id,))
        conn.commit()
        return True, 'Usuario desactivado exitosamente'
    except Exception as e:
        conn.rollback()
        return False, f'Error al desactivar usuario: {str(e)}'
    finally:
        conn.close()

def correo_existe_en_usuarios(correo):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Id FROM tusuarios WHERE correo = %s", (correo,))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def obtener_validacion_pendiente(correo):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, usuario, contrasena, rol_id
                FROM tvalidacion_usuarios WHERE correo = %s AND validado = FALSE
            """, (correo,))
            return cursor.fetchone()
    finally:
        conn.close()

def actualizar_correo_validacion(validacion_id, correo_nuevo, nuevo_codigo):
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE tvalidacion_usuarios SET correo=%s, codigo=%s, fecha_creacion=%s WHERE id=%s",
                          (correo_nuevo, nuevo_codigo, datetime.now(), validacion_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al actualizar correo de validación: {e}")
        return False
    finally:
        conn.close()