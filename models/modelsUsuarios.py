# Modelo de usuarios — CRUD, validación por código y gestión de activos/inactivos
import logging
from datetime import datetime, timedelta
from bd import Conexion_BD
from models.modelsRecuperacion import generar_codigo

logger = logging.getLogger(__name__)


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
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Id FROM tusuarios WHERE correo = %s", (correo,))
            if cursor.fetchone():
                return False, "Ya existe un usuario con ese correo electrónico", None
            
            cursor.execute("SELECT id FROM tvalidacion_usuarios WHERE correo = %s AND validado = FALSE", (correo,))
            if cursor.fetchone():
                return False, "Ya existe una solicitud pendiente para este correo", None
            
            codigo = generar_codigo()
            cursor.execute("""
                INSERT INTO tvalidacion_usuarios (usuario, contrasena, correo, rol_id, codigo, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (usuario, contrasena, correo, rol_id, codigo, datetime.now()))
            
            conn.commit()
            id_validacion = cursor.lastrowid
            return True, "Usuario pendiente de validación", {"id": id_validacion, "codigo": codigo}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al guardar usuario pendiente: {e}")
        return False, f"Error: {str(e)}", None
    finally:
        conn.close()

def validar_codigo_usuario(correo, codigo):
    """Valida el código y crea el usuario definitivo en tusuarios, o actualiza su correo si es un cambio."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, usuario, contrasena, correo, rol_id, fecha_creacion
                FROM tvalidacion_usuarios
                WHERE correo = %s AND codigo = %s AND validado = FALSE
            """, (correo, codigo))
            validacion = cursor.fetchone()
            
            if not validacion:
                return False, "Código de validación incorrecto o expirado"
            
            # Expira a los 30 min
            if datetime.now() - validacion['fecha_creacion'] > timedelta(minutes=30):
                return False, "El código de validación ha expirado"
            
            if validacion['usuario'].startswith('__CAMBIO_CORREO__'):
                # Es un cambio de correo para un usuario existente
                id_usuario_existente = int(validacion['usuario'].replace('__CAMBIO_CORREO__', ''))
                cursor.execute("UPDATE tusuarios SET correo = %s WHERE Id = %s",
                               (validacion['correo'], id_usuario_existente))
                mensaje_exito = "Correo electrónico actualizado y validado correctamente"
            else:
                # Es un nuevo usuario
                cursor.execute("INSERT INTO tusuarios (usuario, contrasena, correo, rol_id) VALUES (%s, %s, %s, %s)",
                               (validacion['usuario'], validacion['contrasena'], validacion['correo'], validacion['rol_id']))
                mensaje_exito = "Usuario validado correctamente"
                
            cursor.execute("DELETE FROM tvalidacion_usuarios WHERE id = %s", (validacion['id'],))
            
            conn.commit()
            return True, mensaje_exito
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al validar código: {e}")
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def reenviar_codigo_validacion(correo):
    """Genera un código nuevo para una solicitud pendiente."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM tvalidacion_usuarios WHERE correo = %s AND validado = FALSE", (correo,))
            validacion = cursor.fetchone()
            
            if not validacion:
                return False, "No se encontró una solicitud pendiente para este correo", None
            
            nuevo_codigo = generar_codigo()
            cursor.execute("UPDATE tvalidacion_usuarios SET codigo = %s, fecha_creacion = %s WHERE id = %s",
                           (nuevo_codigo, datetime.now(), validacion['id']))
            
            conn.commit()
            return True, "Código regenerado correctamente", nuevo_codigo
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al reenviar código: {e}")
        return False, f"Error: {str(e)}", None
    finally:
        conn.close()

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

def guardar_cambio_correo_pendiente(id_usuario, correo_nuevo, codigo):
    """Guarda un cambio de correo pendiente de validación para un usuario existente."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            # Verificar que el nuevo correo no esté en uso
            cursor.execute("SELECT Id FROM tusuarios WHERE correo = %s AND Id != %s", (correo_nuevo, id_usuario))
            if cursor.fetchone():
                return False
            
            # Obtener el rol_id actual del usuario para cumplir con la foreign key
            cursor.execute("SELECT rol_id FROM tusuarios WHERE Id = %s", (id_usuario,))
            rol_row = cursor.fetchone()
            rol_id_actual = rol_row['rol_id'] if rol_row else 1
            
            # Eliminar validaciones previas de cambio de correo para este usuario
            cursor.execute("DELETE FROM tvalidacion_usuarios WHERE usuario = %s AND validado = FALSE", 
                          (f'__CAMBIO_CORREO__{id_usuario}',))
            
            # Insertar nueva validación de cambio de correo
            cursor.execute("""
                INSERT INTO tvalidacion_usuarios (usuario, contrasena, correo, rol_id, codigo, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (f'__CAMBIO_CORREO__{id_usuario}', '', correo_nuevo, rol_id_actual, codigo, datetime.now()))
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al guardar cambio de correo pendiente: {e}")
        return False
    finally:
        conn.close()