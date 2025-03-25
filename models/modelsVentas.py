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

def crear_venta(cliente_id, vendedor_id, total, productos, metodo_pago_id=1, estado_id=1, numero_mesa=''):
    """
    Crea una nueva venta en la base de datos
    
    Args:
        cliente_id: ID del cliente
        vendedor_id: ID del vendedor
        total: Total de la venta
        productos: Lista de productos [{'id': id, 'cantidad': cantidad, 'precio': precio}]
        metodo_pago_id: ID del método de pago (default: 1 - Efectivo)
        estado_id: ID del estado de la venta (default: 1 - Completada)
        numero_mesa: Número de mesa (opcional)
        
    Returns:
        (bool, int): Tupla con éxito de la operación y el ID de la venta creada
    """
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Imprimir valores para depuración
        print(f"Insertando venta: cliente_id={cliente_id}, vendedor_id={vendedor_id}, total={total}, metodo_pago_id={metodo_pago_id}, estado_id={estado_id}, numero_mesa={numero_mesa}")
        
        # Verificar si la tabla tiene una columna para número de mesa
        cursor.execute("DESCRIBE tventas")
        columnas = cursor.fetchall()
        tiene_columna_mesa = any(col['Field'] == 'numero_mesa' for col in columnas)
        
        # Si no existe la columna, agregarla
        if not tiene_columna_mesa:
            cursor.execute("ALTER TABLE tventas ADD COLUMN numero_mesa VARCHAR(10) NULL")
            conn.commit()
            print("Columna numero_mesa agregada a la tabla tventas")
        
        # Usar una consulta que incluya el número de mesa
        if tiene_columna_mesa or True:  # Siempre intentar insertar con la columna
            query_venta = """
            INSERT INTO tventas 
            (cliente_id, vendedor_id, total, metodo_pago_id, estado_id, numero_mesa) 
            VALUES 
            (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_venta, (cliente_id, vendedor_id, total, metodo_pago_id, estado_id, numero_mesa))
        else:
            # Consulta sin número de mesa (por si acaso)
            query_venta = """
            INSERT INTO tventas 
            (cliente_id, vendedor_id, total, metodo_pago_id, estado_id) 
            VALUES 
            (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_venta, (cliente_id, vendedor_id, total, metodo_pago_id, estado_id))
        
        venta_id = cursor.lastrowid
        print(f"ID de venta generado: {venta_id}")
        
        # Insertar los detalles de la venta
        for i, producto in enumerate(productos):
            query_detalle = """
            INSERT INTO tdetalleventas 
            (venta_id, producto_id, cantidad, precio)
            VALUES 
            (%s, %s, %s, %s)
            """
            
            print(f"Insertando detalle {i+1}: venta_id={venta_id}, producto_id={producto['id']}, cantidad={producto['cantidad']}, precio={producto['precio']}")
            cursor.execute(query_detalle, (venta_id, producto['id'], producto['cantidad'], producto['precio']))
            print(f"Detalle {i+1} insertado correctamente")
            
            # Actualizar el stock del producto si es necesario
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
        return False, 0