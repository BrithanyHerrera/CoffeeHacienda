from bd import Conexion_BD
from pymysql.cursors import DictCursor
from flask import request, jsonify

def filtrar_ventas():
    totales = {'efectivo': 0, 'transferencias': 0, 'paypal': 0}
    
    try:
        # Verificar si se reciben datos JSON
        data = request.json
        if not data:
            return jsonify(totales)  # Retorna totales vacíos si no se reciben datos
        
        fecha_desde = data.get('fechaDesde')
        fecha_hasta = data.get('fechaHasta')

        # Verificar si las fechas fueron proporcionadas
        if not fecha_desde or not fecha_hasta:
            print("Las fechas no fueron proporcionadas correctamente.")  # Depuración
            return jsonify(totales)  # Retorna totales vacíos si faltan fechas

        # Establecer la conexión con la base de datos
        connection = Conexion_BD()
        if not connection:
            print("No se pudo conectar a la base de datos")  # Depuración
            return jsonify(totales)  # Retorna totales vacíos si no hay conexión
        else:
            print("Conexión exitosa a la base de datos.")  # Depuración

        # Ejecutar consulta SQL
        with connection.cursor(DictCursor) as cursor:
            query = """
                SELECT metodo_pago_id, SUM(total) AS total
                FROM tventas 
                WHERE fecha_hora BETWEEN %s AND %s
                GROUP BY metodo_pago_id
            """
            cursor.execute(query, (fecha_desde, fecha_hasta))
            resultados = cursor.fetchall()
        
        # Cerrar la conexión
        connection.close()
        
        # Procesar los resultados
        for row in resultados:
            if row['metodo_pago_id'] == 1:
                totales['efectivo'] = row['total']
            elif row['metodo_pago_id'] == 2:
                totales['transferencias'] = row['total']
            elif row['metodo_pago_id'] == 3:
                totales['paypal'] = row['total']
        
    except Exception as e:
        print(f"Error al filtrar ventas: {e}")  # Depuración
    
    return jsonify(totales)

def guardar_corte_caja(
    vendedor_id, fecha_inicio, fecha_cierre,
    total_ventas, total_efectivo,
    total_transferencias, total_paypal, total_contado,
    pagos_realizados, fondo
):
    resultado = False

    try:
        if pagos_realizados < total_ventas:
            # Hay ganancia
            ganancia_o_perdida = total_ventas - pagos_realizados
        else:
            # Hay pérdida
            if pagos_realizados > total_ventas:
                ganancia_o_perdida = total_ventas - pagos_realizados
            else:
                ganancia_o_perdida = 0  # No hay ni ganancia ni pérdida


        connection = Conexion_BD()
        with connection.cursor() as cursor:
            query = """
            INSERT INTO tcortescaja (
                vendedor_id, fecha_hora_inicio, fecha_hora_cierre,
                total_ventas, total_efectivo,
                total_transferencias, total_paypal, total_contado, pagos_realizados, fondo,
                ganancia_o_perdida
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                vendedor_id, fecha_inicio, fecha_cierre,
                total_ventas, total_efectivo,
                total_transferencias, total_paypal, total_contado,
                pagos_realizados, fondo, ganancia_o_perdida
            )
            cursor.execute(query, valores)
        connection.commit()
        resultado = True
        connection.close()
    except Exception as e:
        print(f"Error al guardar corte de caja: {e}")

    return resultado

def obtener_corte_por_id(id):
    connection = Conexion_BD()
    try:
        with connection.cursor(dictionary=True) as cursor:
            sql = """
                SELECT 
                    c.id,
                    c.vendedor_id,
                    u.nombre_usuario AS nombre_vendedor,
                    c.fecha_hora_inicio,
                    c.fecha_hora_cierre,
                    c.total_ventas,
                    c.total_efectivo,
                    c.total_transferencias,
                    c.total_paypal,
                    c.total_contado,
                    c.pagos_realizados,
                    c.fondo,
                    c.ganancia_o_perdida
                FROM tcortescaja c
                JOIN tusuarios u ON c.vendedor_id = u.Id
                WHERE c.id = %s
            """
            cursor.execute(sql, (id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener corte de caja por ID: {e}")
        return None
    finally:
        connection.close()


