import random
import string
from datetime import datetime, timedelta
from bd import Conexion_BD

def verificar_usuario_existente(usuario):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) as count FROM tusuarios WHERE usuario = %s"
            cursor.execute(sql, (usuario,))
            resultado = cursor.fetchone()
            return resultado['count'] > 0
    except Exception as e:
        print(f"Error al verificar usuario existente: {e}")
        return False
    finally:
        connection.close()

def verificar_correo_existente(correo):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) as count FROM tusuarios WHERE correo = %s"
            cursor.execute(sql, (correo,))
            resultado = cursor.fetchone()
            return resultado['count'] > 0
    except Exception as e:
        print(f"Error al verificar correo existente: {e}")
        return False
    finally:
        connection.close()

def crear_usuario(usuario, contrasena, correo, rol_id):
    # Verificar si el usuario o correo ya existen
    if verificar_usuario_existente(usuario):
        return False, "El nombre de usuario ya está en uso"
    
    if verificar_correo_existente(correo):
        return False, "El correo electrónico ya está registrado"
    
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            # Insertar el usuario con el correo directamente
            sql = "INSERT INTO tusuarios (usuario, contrasena, rol_id, correo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (usuario, contrasena, rol_id, correo))
            
        connection.commit()
        return True, "Usuario creado exitosamente"
    except Exception as e:
        connection.rollback()
        print(f"Error al crear usuario: {e}")
        return False, f"Error al crear usuario: {str(e)}"
    finally:
        connection.close()

def obtener_usuarios():
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT u.Id, u.usuario, u.contrasena, u.correo, r.rol, r.Id as rol_id, u.creado_en 
                FROM tusuarios u 
                JOIN troles r ON u.rol_id = r.Id
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        connection.close()

def actualizar_usuario(id, usuario, contrasena, correo, rol_id):
    # Verificar si el usuario ya existe para otro usuario
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            # Verificar si el usuario ya está en uso por otro usuario
            sql = "SELECT COUNT(*) as count FROM tusuarios WHERE usuario = %s AND Id != %s"
            cursor.execute(sql, (usuario, id))
            resultado = cursor.fetchone()
            
            if resultado['count'] > 0:
                print(f"Error: El usuario '{usuario}' ya está en uso por otro usuario")
                return False, "El nombre de usuario ya está en uso por otro usuario"
            
            # Verificar si el correo ya está en uso por otro usuario
            sql = "SELECT COUNT(*) as count FROM tusuarios WHERE correo = %s AND Id != %s"
            cursor.execute(sql, (correo, id))
            resultado = cursor.fetchone()
            
            if resultado['count'] > 0:
                print(f"Error: El correo '{correo}' ya está registrado por otro usuario")
                return False, "El correo electrónico ya está registrado por otro usuario"
            
            # Actualizar usuario con el correo directamente
            sql = "UPDATE tusuarios SET usuario = %s, contrasena = %s, rol_id = %s, correo = %s WHERE Id = %s"
            cursor.execute(sql, (usuario, contrasena, rol_id, correo, id))

        connection.commit()
        return True, "Usuario actualizado exitosamente"
    except Exception as e:
        connection.rollback()
        print(f"Error al actualizar usuario: {e}")
        return False, f"Error al actualizar usuario: {str(e)}"
    finally:
        connection.close()

def eliminar_usuario(id):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            # Delete user directly
            sql = "DELETE FROM tusuarios WHERE Id=%s"
            cursor.execute(sql, (id,))
            
        connection.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False
    finally:
        connection.close()

def obtener_usuario_por_id(id):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT u.*, r.rol
                FROM tusuarios u 
                JOIN troles r ON u.rol_id = r.Id 
                WHERE u.Id=%s
            """
            cursor.execute(sql, (id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener usuario por ID: {e}")
        return None
    finally:
        connection.close()

def obtener_roles():
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM troles"
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener roles: {e}")
        return []
    finally:
        connection.close()

def obtener_usuario_por_correo(correo):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT u.*, r.rol
                FROM tusuarios u 
                JOIN troles r ON u.rol_id = r.Id 
                WHERE u.correo = %s
            """
            cursor.execute(sql, (correo,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener usuario por correo: {e}")
        return None
    finally:
        connection.close()


def generar_codigo_validacion():
    """Genera un código aleatorio de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

def guardar_usuario_pendiente(usuario, contrasena, correo, rol_id):
    """Guarda un usuario pendiente de validación y genera un código"""
    try:
        # Verificar si ya existe un usuario con ese correo
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Verificar en la tabla de usuarios
        cursor.execute("SELECT Id FROM tusuarios WHERE correo = %s", (correo,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Ya existe un usuario con ese correo electrónico", None
        
        # Verificar en la tabla de validación
        cursor.execute("SELECT id FROM tvalidacion_usuarios WHERE correo = %s AND validado = FALSE", (correo,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Ya existe una solicitud pendiente para este correo", None
        
        # Generar código de validación
        codigo = generar_codigo_validacion()
        
        # Guardar en la tabla de validación
        cursor.execute("""
            INSERT INTO tvalidacion_usuarios 
            (usuario, contrasena, correo, rol_id, codigo, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario, contrasena, correo, rol_id, codigo, datetime.now()))
        
        conn.commit()
        id_validacion = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return True, "Usuario pendiente de validación", {"id": id_validacion, "codigo": codigo}
    except Exception as e:
        print(f"Error al guardar usuario pendiente: {e}")
        return False, f"Error: {str(e)}", None

def validar_codigo_usuario(correo, codigo):
    """Valida el código de un usuario pendiente"""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Buscar el registro de validación
        cursor.execute("""
            SELECT id, usuario, contrasena, correo, rol_id, fecha_creacion
            FROM tvalidacion_usuarios
            WHERE correo = %s AND codigo = %s AND validado = FALSE
        """, (correo, codigo))
        
        validacion = cursor.fetchone()
        
        if not validacion:
            cursor.close()
            conn.close()
            return False, "Código de validación incorrecto o expirado"
        
        # Verificar si el código ha expirado (30 minutos)
        fecha_creacion = validacion['fecha_creacion']
        if datetime.now() - fecha_creacion > timedelta(minutes=30):
            cursor.close()
            conn.close()
            return False, "El código de validación ha expirado"
        
        # Crear el usuario en la tabla de usuarios
        cursor.execute("""
            INSERT INTO tusuarios (usuario, contrasena, correo, rol_id)
            VALUES (%s, %s, %s, %s)
        """, (validacion['usuario'], validacion['contrasena'], validacion['correo'], validacion['rol_id']))
        
        # Eliminar el registro de validación en lugar de marcarlo como validado
        cursor.execute("""
            DELETE FROM tvalidacion_usuarios
            WHERE id = %s
        """, (validacion['id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "Usuario validado correctamente"
    except Exception as e:
        print(f"Error al validar código: {e}")
        return False, f"Error: {str(e)}"

def reenviar_codigo_validacion(correo):
    """Regenera y devuelve un nuevo código de validación"""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Buscar el registro de validación
        cursor.execute("""
            SELECT id
            FROM tvalidacion_usuarios
            WHERE correo = %s AND validado = FALSE
        """, (correo,))
        
        validacion = cursor.fetchone()
        
        if not validacion:
            cursor.close()
            conn.close()
            return False, "No se encontró una solicitud pendiente para este correo", None
        
        # Generar nuevo código
        nuevo_codigo = generar_codigo_validacion()
        
        # Actualizar el código y la fecha
        cursor.execute("""
            UPDATE tvalidacion_usuarios
            SET codigo = %s, fecha_creacion = %s
            WHERE id = %s
        """, (nuevo_codigo, datetime.now(), validacion['id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "Código regenerado correctamente", nuevo_codigo
    except Exception as e:
        print(f"Error al reenviar código: {e}")
        return False, f"Error: {str(e)}", None

def limpiar_validaciones_expiradas():
    """Elimina las validaciones que han expirado (más de 30 minutos)"""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Eliminar registros expirados (más de 30 minutos)
        cursor.execute("""
            DELETE FROM tvalidacion_usuarios
            WHERE validado = FALSE AND fecha_creacion < %s
        """, (datetime.now() - timedelta(minutes=30),))
        
        registros_eliminados = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return registros_eliminados
    except Exception as e:
        print(f"Error al limpiar validaciones expiradas: {e}")
        return 0