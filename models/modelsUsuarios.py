from bd import Conexion_BD

def crear_usuario(usuario, contrasena, correo, rol_id):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            # Insertar el usuario con el correo directamente
            sql = "INSERT INTO tusuarios (usuario, contrasena, rol_id, correo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (usuario, contrasena, rol_id, correo))
            
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error al crear usuario: {e}")
        return False
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
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            # Actualizar usuario con el correo directamente
            sql = "UPDATE tusuarios SET usuario = %s, contrasena = %s, rol_id = %s, correo = %s WHERE Id = %s"
            cursor.execute(sql, (usuario, contrasena, rol_id, correo, id))

        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error al actualizar usuario: {e}")
        return False
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