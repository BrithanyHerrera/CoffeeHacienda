from bd import Conexion_BD

def obtener_historial_ventas(filtro_cliente=None, fecha_inicio=None, fecha_fin=None):
    """Obtiene el historial de ventas con filtros opcionales."""
    db = Conexion_BD()  # Conexión directa
    cursor = db.cursor()  # Obtenemos el cursor

    query = """
        SELECT v.id, v.fecha_hora, v.total, u.usuario AS vendedor, c.nombre AS cliente, v.numero_mesa
        FROM tventas v
        JOIN tusuarios u ON v.vendedor_id = u.id
        JOIN tclientes c ON v.cliente_id = c.id
        WHERE 1=1
    """
    params = []

    if filtro_cliente:
        query += " AND c.nombre LIKE %s"
        params.append(f"%{filtro_cliente}%")
    
    if fecha_inicio:
        query += " AND v.fecha_hora >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND v.fecha_hora <= %s"
        params.append(fecha_fin)

    query += " ORDER BY v.fecha_hora DESC"

    cursor.execute(query, params)
    ventas = cursor.fetchall()
    db.close()  # Cerramos la conexión
    return ventas

def obtener_detalle_venta(id_venta):
    """Obtiene los detalles de una venta específica."""
    db = Conexion_BD()
    cursor = db.cursor()

    query = """
        SELECT v.id, v.fecha_hora, v.total, u.usuario AS vendedor, c.nombre AS cliente, 
               p.nombre_producto, dv.cantidad, dv.precio AS precio_unitario, v.numero_mesa
        FROM tventas v
        JOIN tusuarios u ON v.vendedor_id = u.id
        JOIN tclientes c ON v.cliente_id = c.id
        JOIN tdetalleventas dv ON v.id = dv.venta_id
        JOIN tproductos p ON dv.producto_id = p.id
        WHERE v.id = %s
    """

    cursor.execute(query, (id_venta,))
    detalles = cursor.fetchall()
    db.close()  # Cerramos la conexión
    return detalles
