# Modelo de historial — ventas completadas, canceladas y reembolsadas
import logging
from bd import Conexion_BD

logger = logging.getLogger(__name__)

def obtener_historial_ventas(filtro_cliente=None, filtro_vendedor=None, fecha_inicio=None, fecha_fin=None):
    """Obtiene el historial con filtros opcionales por cliente, vendedor y rango de fechas."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT v.id, v.fecha_hora, v.total, u.usuario AS vendedor, c.nombre AS cliente,
               v.numero_mesa, e.estado, m.tipo_de_pago AS metodo_pago
        FROM tventas v
        JOIN tusuarios u ON v.vendedor_id = u.id
        JOIN tclientes c ON v.cliente_id = c.id
        JOIN testadosventa e ON v.estado_id = e.id
        JOIN tmetodospago m ON v.metodo_pago_id = m.id
        WHERE v.estado_id IN (3, 4, 5)
        """
        
        params = []
        
        if filtro_cliente:
            query += " AND c.nombre LIKE %s"
            params.append(f"%{filtro_cliente}%")
        
        if filtro_vendedor:
            query += " AND u.usuario = %s"
            params.append(filtro_vendedor)
        
        if fecha_inicio:
            query += " AND DATE(v.fecha_hora) >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND DATE(v.fecha_hora) <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY v.fecha_hora DESC"
        
        cursor.execute(query, params)
        ventas = cursor.fetchall()
        
        cursor.close()
        return ventas
    except Exception as e:
        logger.error(f"Error al obtener historial de ventas: {e}", exc_info=True)
        return []
    finally:
        conn.close()