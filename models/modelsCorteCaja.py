# Corte de caja: consultas y registros
import logging
from decimal import Decimal
from bd import Conexion_BD
from services.auditoria import registrar_evento

logger = logging.getLogger(__name__)


def filtrar_ventas(fecha_desde, fecha_hasta):
    """Suma totales por método de pago en un rango de fechas."""
    totales = {
        'efectivo': Decimal('0.00'),
        'tarjeta': Decimal('0.00'),
        'transferencias': Decimal('0.00'),
    }

    try:
        if not fecha_desde or not fecha_hasta:
            return totales

        conn = Conexion_BD()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT mp.codigo, SUM(v.total) AS total
                    FROM tventas v
                    JOIN tmetodospago mp ON mp.Id = v.metodo_pago_id
                    WHERE v.fecha_hora BETWEEN %s AND %s
                      AND v.estado_id = 4
                    GROUP BY mp.codigo
                """, (fecha_desde, fecha_hasta))
                
                for row in cursor.fetchall():
                    if row['codigo'] == 'EFECTIVO':
                        totales['efectivo'] = row['total']
                    elif row['codigo'] == 'TARJETA':
                        totales['tarjeta'] = row['total']
                    elif row['codigo'] == 'TRANSFERENCIA':
                        totales['transferencias'] = row['total']
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error al filtrar ventas: {e}")

    return totales


def obtener_todos_cortes():
    """Lista todos los cortes (sin ganancia/pérdida)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Id, fecha_hora_inicio, fecha_hora_cierre, fondo, total_contado, total_ventas, pagos_realizados
                FROM tcortescaja ORDER BY fecha_hora_cierre DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def obtener_cortes_con_ganancia():
    """Lista todos los cortes incluyendo ganancia/pérdida (para reportes)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Id, fecha_hora_cierre, fondo, total_contado, total_ventas,
                       pagos_realizados, ganancia_o_perdida
                FROM tcortescaja ORDER BY fecha_hora_cierre DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def guardar_corte_caja(vendedor_id, fecha_inicio, fecha_cierre, total_ventas,
                       total_efectivo, total_transferencias, total_tarjeta,
                       total_contado, pagos_realizados, fondo):
    """Registra un corte de caja. Calcula ganancia automáticamente."""
    try:
        ganancia = Decimal(total_ventas) - Decimal(pagos_realizados)

        conn = Conexion_BD()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT Id FROM tcortescaja
                    WHERE fecha_hora_inicio < %s AND fecha_hora_cierre > %s
                    LIMIT 1
                    FOR UPDATE
                """, (fecha_cierre, fecha_inicio))
                if cursor.fetchone():
                    conn.rollback()
                    return False, 'Ya existe un corte que se cruza con ese periodo', None

                cursor.execute("""
                    INSERT INTO tcortescaja (
                        vendedor_id, fecha_hora_inicio, fecha_hora_cierre,
                        total_ventas, total_efectivo, total_transferencias, total_tarjeta,
                        total_contado, pagos_realizados, fondo, ganancia_o_perdida
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (vendedor_id, fecha_inicio, fecha_cierre, total_ventas,
                      total_efectivo, total_transferencias, total_tarjeta,
                      total_contado, pagos_realizados, fondo, ganancia))
                corte_id = cursor.lastrowid
                registrar_evento(cursor, 'CREAR', 'corte_caja', corte_id,
                                 usuario_id=vendedor_id,
                                 detalles={'total_ventas': str(total_ventas),
                                           'ganancia': str(ganancia)})
            conn.commit()
            return True, 'Corte registrado correctamente', corte_id
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error al guardar corte de caja: {e}")
        return False, 'No se pudo registrar el corte', None


def obtener_corte_por_id(id):
    """Obtiene un corte específico con el nombre del vendedor."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.vendedor_id, u.usuario AS nombre_vendedor,
                       c.fecha_hora_inicio, c.fecha_hora_cierre,
                        c.total_ventas, c.total_efectivo, c.total_transferencias, c.total_tarjeta,
                       c.total_contado, c.pagos_realizados, c.fondo, c.ganancia_o_perdida
                FROM tcortescaja c
                JOIN tusuarios u ON c.vendedor_id = u.Id
                WHERE c.id = %s
            """, (id,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener corte por ID: {e}")
        return None
    finally:
        conn.close()
