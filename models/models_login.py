from bd import Conexion_BD

def verificar_usuario(usuario, contrasena):
    connection = Conexion_BD()  # Establecer la conexión
    try:
        with connection.cursor() as cursor:
            # Consulta para obtener el usuario desde la base de datos
            sql = "SELECT * FROM tusuarios WHERE usuario = %s"
            cursor.execute(sql, (usuario,))  # Ejecutar la consulta
            user = cursor.fetchone()  # Obtener el primer resultado
            
            # Verificar si se encontró el usuario y si las contraseñas coinciden
            if user and user['contrasena'] == contrasena:
                return True  # Usuario encontrado y contraseña correcta
            else:
                return False  # Usuario no encontrado o contraseña incorrecta
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        return False
    finally:
        connection.close()  # Cerrar la conexión
