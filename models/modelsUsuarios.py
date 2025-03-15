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
    # Verificar si el usuario ya existe
    if verificar_usuario_existente(usuario):
        print(f"Error: El usuario '{usuario}' ya existe")
        return False, "El nombre de usuario ya está en uso"
    
    # Verificar si el correo ya existe
    if verificar_correo_existente(correo):
        print(f"Error: El correo '{correo}' ya está registrado")
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
    # Verificar si el correo ya existe para otro usuario
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
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