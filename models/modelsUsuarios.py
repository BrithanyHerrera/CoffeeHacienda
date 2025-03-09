from bd import Conexion_BD

def crear_usuario(usuario, contrasena, correo, rol_id):
    connection = Conexion_BD()
    try:
        connection.begin()
        with connection.cursor() as cursor:
            # Primero insertar el correo si existe
            correo_id = None
            if correo and correo.strip():
                sql_correo = "INSERT INTO tcorreos (correo) VALUES (%s)"
                cursor.execute(sql_correo, (correo,))
                correo_id = cursor.lastrowid

            # Luego insertar el usuario con la referencia al correo
            sql = "INSERT INTO tusuarios (usuario, contrasena, rol_id, id_correo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (usuario, contrasena, rol_id, correo_id))
            
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
                SELECT u.Id, u.usuario, u.contrasena, c.correo, r.rol, r.Id as rol_id, u.creado_en 
                FROM tusuarios u 
                JOIN troles r ON u.rol_id = r.Id
                LEFT JOIN tcorreos c ON u.id_correo = c.Id
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
        connection.begin()
        with connection.cursor() as cursor:
            # Obtener el id_correo actual del usuario
            sql_get_correo = "SELECT id_correo FROM tusuarios WHERE Id = %s"
            cursor.execute(sql_get_correo, (id,))
            result = cursor.fetchone()
            current_correo_id = result['id_correo'] if result else None

            # Actualizar o crear correo
            if correo and correo.strip():
                if current_correo_id:
                    sql_correo = "UPDATE tcorreos SET correo = %s WHERE Id = %s"
                    cursor.execute(sql_correo, (correo, current_correo_id))
                else:
                    sql_correo = "INSERT INTO tcorreos (correo) VALUES (%s)"
                    cursor.execute(sql_correo, (correo,))
                    current_correo_id = cursor.lastrowid

            # Actualizar usuario
            sql = "UPDATE tusuarios SET usuario = %s, contrasena = %s, rol_id = %s, id_correo = %s WHERE Id = %s"
            cursor.execute(sql, (usuario, contrasena, rol_id, current_correo_id, id))

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
            # Delete email first to maintain referential integrity
            sql_correo = "DELETE FROM tcorreos WHERE Id=%s"
            cursor.execute(sql_correo, (id,))
            
            # Then delete user
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
                SELECT u.*, r.rol, c.correo
                FROM tusuarios u 
                JOIN troles r ON u.rol_id = r.Id 
                LEFT JOIN tcorreos c ON c.Id = u.Id
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