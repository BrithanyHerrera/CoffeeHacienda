from bd import Conexion_BD
from datetime import datetime

def obtener_historial_ventas(filtro_cliente=None, fecha_inicio=None, fecha_fin=None):
    """Obtiene el historial de ventas completadas o canceladas con filtros opcionales."""
    db = Conexion_BD()  # Conexión directa
    cursor = db.cursor()  # Obtenemos el cursor
    
    # Construir la consulta base
    query = """
    SELECT v.id, v.fecha_hora, v.total, u.usuario AS vendedor, c.nombre AS cliente,
           v.numero_mesa, e.estado, m.tipo_de_pago AS metodo_pago
    FROM tventas v
    JOIN tusuarios u ON v.vendedor_id = u.id
    JOIN tclientes c ON v.cliente_id = c.id
    JOIN testadosventa e ON v.estado_id = e.id
    JOIN tmetodospago m ON v.metodo_pago_id = m.id
    WHERE v.estado_id IN (3, 4, 5)  -- Completado (4), Cancelado (3) o Reembolsada (5)
    """
    
    # Agregar condiciones de filtro si existen
    params = []
    
    if filtro_cliente:
        query += " AND c.nombre LIKE %s"
        params.append(f"%{filtro_cliente}%")
    
    if fecha_inicio:
        query += " AND DATE(v.fecha_hora) >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND DATE(v.fecha_hora) <= %s"
        params.append(fecha_fin)
    
    # Ordenar por fecha descendente
    query += " ORDER BY v.fecha_hora DESC"
    
    # Ejecutar la consulta
    cursor.execute(query, params)
    ventas = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return ventas

def obtener_detalle_venta(venta_id):
    """Obtiene los detalles de una venta específica."""
    db = Conexion_BD()
    cursor = db.cursor()
    
    query = """
    SELECT d.id, d.venta_id, d.producto_id, p.nombre_producto, d.cantidad, d.precio,
           (d.cantidad * d.precio) AS subtotal, t.tamano
    FROM tdetalleventas d
    JOIN tproductos p ON d.producto_id = p.id
    LEFT JOIN tproductos_variantes pv ON p.id = pv.producto_id
    LEFT JOIN ttamanos t ON pv.tamano_id = t.id
    WHERE d.venta_id = %s
    """
    
    cursor.execute(query, (venta_id,))
    detalles = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return detalles