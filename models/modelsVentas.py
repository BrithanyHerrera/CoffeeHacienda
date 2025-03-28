from bd import Conexion_BD
from datetime import datetime

def obtener_cliente_por_nombre(nombre_cliente):
    """
    Obtiene el ID del cliente por su nombre, o crea uno nuevo si no existe
    
    Args:
        nombre_cliente: Nombre del cliente
        
    Returns:
        int: ID del cliente
    """
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Buscar si el cliente ya existe
        cursor.execute("SELECT Id FROM tclientes WHERE nombre = %s", (nombre_cliente,))
        cliente = cursor.fetchone()
        
        if cliente:
            cliente_id = cliente['Id']
        else:
            # Crear nuevo cliente
            cursor.execute("INSERT INTO tclientes (nombre) VALUES (%s)", (nombre_cliente,))
            cliente_id = cursor.lastrowid
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return cliente_id
    except Exception as e:
        print(f"Error al obtener/crear cliente: {e}")
        return 1  # Cliente por defecto

def crear_venta(cliente_id, vendedor_id, total, productos, metodo_pago_id=1, numero_mesa='', estado_id=4):
    """
    Crea una nueva venta en la base de datos.
    
    Args:
        cliente_id: ID del cliente
        vendedor_id: ID del vendedor
        total: Total de la venta
        productos: Lista de diccionarios con id, cantidad y precio de cada producto
        metodo_pago_id: ID del método de pago (1=Efectivo por defecto)
        numero_mesa: Número de mesa (opcional)
        estado_id: Estado de la venta (4=Completado por defecto)
        
    Returns:
        Tupla (éxito, id_venta)
    """
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Imprimir valores para depuración
        print(f"Insertando venta: cliente_id={cliente_id}, vendedor_id={vendedor_id}, total={total}, metodo_pago_id={metodo_pago_id}, estado_id={estado_id}, numero_mesa={numero_mesa}")
        
        # Insertar la venta
        query = """
        INSERT INTO tventas (cliente_id, vendedor_id, total, metodo_pago_id, numero_mesa, estado_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (cliente_id, vendedor_id, total, metodo_pago_id, numero_mesa, estado_id))
        
        venta_id = cursor.lastrowid
        
        # Insertar los detalles de la venta
        for producto in productos:
            # Insertar detalle de venta
            query_detalle = """
            INSERT INTO tdetalleventas (venta_id, producto_id, cantidad, precio)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_detalle, (venta_id, producto['id'], producto['cantidad'], producto['precio']))
            
            # Actualizar el stock solo si la categoría requiere inventario
            query_stock = """
            UPDATE tproductos p
            JOIN tcategorias c ON p.categoria_id = c.Id
            SET p.stock = p.stock - %s
            WHERE p.Id = %s AND c.requiere_inventario = 1
            """
            cursor.execute(query_stock, (producto['cantidad'], producto['id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, venta_id
        
    except Exception as e:
        print(f"Error al crear venta: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return False, None