# Modelo de corte de caja — consultas y registro de cortes
import logging
from bd import Conexion_BD
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


def filtrar_ventas(fecha_desde, fecha_hasta):
    """Suma totales por método de pago en un rango de fechas."""
    totales = {'efectivo': 0, 'transferencias': 0, 'paypal': 0}

    try:
        if not fecha_desde or not fecha_hasta:
            return totales

        conn = Conexion_BD()
        try:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT metodo_pago_id, SUM(total) AS total
                    FROM tventas 
                    WHERE fecha_hora BETWEEN %s AND %s
                    GROUP BY metodo_pago_id
                """, (fecha_desde, fecha_hasta))
                
                for row in cursor.fetchall():
                    if row['metodo_pago_id'] == 1:
                        totales['efectivo'] = row['total']
                    elif row['metodo_pago_id'] == 2:
                        totales['transferencias'] = row['total']
                    elif row['metodo_pago_id'] == 3:
                        totales['paypal'] = row['total']
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
                SELECT fecha_hora_cierre, fondo, total_contado, total_ventas, pagos_realizados
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
                SELECT fecha_hora_cierre, fondo, total_contado, total_ventas, 
                       pagos_realizados, ganancia_o_perdida
                FROM tcortescaja ORDER BY fecha_hora_cierre DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def guardar_corte_caja(vendedor_id, fecha_inicio, fecha_cierre, total_ventas,
                       total_efectivo, total_transferencias, total_paypal,
                       total_contado, pagos_realizados, fondo):
    """Registra un corte de caja. Calcula ganancia automáticamente."""
    try:
        ganancia = total_ventas - pagos_realizados

        conn = Conexion_BD()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tcortescaja (
                        vendedor_id, fecha_hora_inicio, fecha_hora_cierre,
                        total_ventas, total_efectivo, total_transferencias, total_paypal,
                        total_contado, pagos_realizados, fondo, ganancia_o_perdida
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (vendedor_id, fecha_inicio, fecha_cierre, total_ventas,
                      total_efectivo, total_transferencias, total_paypal,
                      total_contado, pagos_realizados, fondo, ganancia))
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error al guardar corte de caja: {e}")
        return False


def obtener_corte_por_id(id):
    """Obtiene un corte específico con el nombre del vendedor."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.vendedor_id, u.usuario AS nombre_vendedor,
                       c.fecha_hora_inicio, c.fecha_hora_cierre,
                       c.total_ventas, c.total_efectivo, c.total_transferencias, c.total_paypal,
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
