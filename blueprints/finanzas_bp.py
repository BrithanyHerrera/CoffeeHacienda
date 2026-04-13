from flask import Blueprint, render_template, request, jsonify, session
from bd import Conexion_BD
from utils import login_required, admin_required
from models.modelsCorteCaja import (filtrar_ventas, guardar_corte_caja, obtener_corte_por_id)

finanzas_bp = Blueprint('finanzas', __name__)

@finanzas_bp.route('/filtrarVentas', methods=['POST'])
def filtrar_ventas_route():
    return filtrar_ventas()

@finanzas_bp.route('/corteCaja', methods=['GET', 'POST'])
@login_required 
@admin_required 
def corte():
    nombre_usuario = session['usuario']
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario (no JSON)
            fecha_inicio = request.form.get('fecha_hora_inicio')
            fecha_cierre = request.form.get('fecha_hora_cierre')
            total_ventas = float(request.form.get('total_ventas', 0))
            total_efectivo = float(request.form.get('total_efectivo', 0))
            total_transferencias = float(request.form.get('total_transferencias', 0))
            total_paypal = float(request.form.get('total_paypal', 0))
            total_contado = float(request.form.get('total_contado', 0))
            pagos_realizados = float(request.form.get('pagos_realizados', 0))

            # Obtener el ID del vendedor desde la sesión
            vendedor_id = session.get('usuario_id')

            # Llamar a la función de modelo para guardar el corte de caja en la base de datos
            resultado, error = guardar_corte_caja(
                vendedor_id, fecha_inicio, fecha_cierre,
                total_ventas, total_efectivo,
                total_transferencias, total_paypal,
                total_contado, pagos_realizados
            )

            if resultado:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": error})

        except Exception as e:
            return jsonify({"success": False, "error": f"Error al guardar el corte: {str(e)}"}), 500

    # Si es un GET, mostrar la página de corte con el historial de cortes anteriores
    conexion = Conexion_BD()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT fecha_hora_cierre, fondo, total_contado, total_ventas, pagos_realizados
                FROM TCortesCaja
                ORDER BY fecha_hora_cierre DESC
            """)
            cortes = cursor.fetchall()
    finally:
        conexion.close()

    return render_template('corteCaja.html', cortes=cortes, nombre_usuario=nombre_usuario)

@finanzas_bp.route('/api/corteCaja/<int:id>', methods=['GET'])
@login_required
def get_corte_caja(id):
    try:
        corte = obtener_corte_por_id(id)
        if corte:
            return jsonify({
                'success': True,
                'corte': corte
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Corte de caja no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@finanzas_bp.route('/guardarCorteCaja', methods=['POST'])
@login_required
def guardar_corte():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)

        vendedor_id = session.get('usuario_id')

        # Recolectar los datos enviados desde el formulario o JS
        fecha_inicio = data.get('fecha_hora_inicio')
        fecha_cierre = data.get('fecha_hora_cierre')
        total_ventas = float(data.get('total_ventas', 0))
        total_efectivo = float(data.get('total_efectivo', 0))
        total_transferencias = float(data.get('total_transferencias', 0))
        total_paypal = float(data.get('total_paypal', 0))
        total_contado = float(data.get('total_contado', 0))
        pagos_realizados = float(data.get('pagos_realizados', 0))
        fondo = float(data.get('fondo', 0))

        # Guardar el corte en la base de datos
        exito = guardar_corte_caja(
            vendedor_id, fecha_inicio, fecha_cierre,
            total_ventas, total_efectivo,
            total_transferencias, total_paypal, total_contado,
            pagos_realizados, fondo
        )

        if exito:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al guardar el corte"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": f"Error en la ruta /guardarCorteCaja: {str(e)}"}), 500 

@finanzas_bp.route('/reporteFinanciero')
@login_required
def reporte():
    conexion = Conexion_BD()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT fecha_hora_cierre, fondo, total_contado, total_ventas, pagos_realizados, ganancia_o_perdida
            FROM TCortesCaja
            ORDER BY fecha_hora_cierre DESC
        """)
        cortes = cursor.fetchall()

    return render_template('reportesFinancieros.html', cortes=cortes)
