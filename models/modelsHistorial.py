# Historial: ventas completadas, canceladas y reembolsadas
import logging
from bd import Conexion_BD

logger = logging.getLogger(__name__)

def obtener_historial_ventas(filtro_cliente=None, filtro_vendedor=None, fecha_inicio=None, fecha_fin=None, pagina=1, por_pagina=15):
    """Obtiene el historial con filtros opcionales y paginación. Retorna (ventas, total_paginas, total_ventas)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            # Base query con filtros
            where_clause = "WHERE v.estado_id IN (3, 4, 5)"
            params = []
            
            if filtro_cliente:
                where_clause += " AND c.nombre LIKE %s"
                params.append(f"%{filtro_cliente}%")
            
            if filtro_vendedor:
                where_clause += " AND u.usuario = %s"
                params.append(filtro_vendedor)
            
            if fecha_inicio:
                where_clause += " AND DATE(v.fecha_hora) >= %s"
                params.append(fecha_inicio)
            
            if fecha_fin:
                where_clause += " AND DATE(v.fecha_hora) <= %s"
                params.append(fecha_fin)
            
            # Contar total de resultados
            count_query = f"""
                SELECT COUNT(*) as total
                FROM tventas v
                JOIN tusuarios u ON v.vendedor_id = u.id
                JOIN tclientes c ON v.cliente_id = c.id
                {where_clause}
            """
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Calcular paginación
            total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
            pagina = max(1, min(pagina, total_paginas))
            offset = (pagina - 1) * por_pagina
            
            # Query principal con LIMIT/OFFSET
            query = f"""
                SELECT v.id, v.fecha_hora, v.total, u.usuario AS vendedor, c.nombre AS cliente,
                       v.numero_mesa, e.estado, m.tipo_de_pago AS metodo_pago
                FROM tventas v
                JOIN tusuarios u ON v.vendedor_id = u.id
                JOIN tclientes c ON v.cliente_id = c.id
                JOIN testadosventa e ON v.estado_id = e.id
                JOIN tmetodospago m ON v.metodo_pago_id = m.id
                {where_clause}
                ORDER BY v.fecha_hora DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [por_pagina, offset])
            ventas = cursor.fetchall()
            
            return ventas, total_paginas, total
    except Exception as e:
        logger.error(f"Error al obtener historial de ventas: {e}", exc_info=True)
        return [], 1, 0
    finally:
        conn.close()