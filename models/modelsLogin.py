from bd import Conexion_BD

def verificar_usuario(usuario, contrasena):
    conn = Conexion_BD()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rol_id 
        FROM tusuarios 
        WHERE usuario = %s 
        AND contrasena = %s
        AND activo = 1  # Solo usuarios activos
    """, (usuario, contrasena))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if resultado:
        return True, resultado['rol_id']  # Devuelve True y el rol_id
    return False, None  # Devuelve False si no es válido o está inactivo
