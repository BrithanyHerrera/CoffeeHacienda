# Modelo de login — búsqueda de usuario para autenticación
from bd import Conexion_BD


def buscar_usuario_por_usuario(usuario):
    """Busca un usuario por nombre y devuelve su info (Id, activo, contrasena, rol)."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.Id, u.activo, u.contrasena, r.rol 
            FROM tusuarios u
            JOIN troles r ON u.rol_id = r.Id
            WHERE u.usuario = %s
        """, (usuario,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado
    finally:
        conn.close()
