# Rutas de finanzas — corte de caja y reportes de ventas
from flask import Blueprint, render_template, request, jsonify, session
from utils import login_required, admin_required
from models.modelsCorteCaja import (filtrar_ventas, guardar_corte_caja, obtener_corte_por_id,
                                     obtener_todos_cortes, obtener_cortes_con_ganancia)

finanzas_bp = Blueprint('finanzas', __name__)

@finanzas_bp.route('/filtrarVentas', methods=['POST'])
@login_required
def filtrar_ventas_route():
    data = request.json
    fecha_desde = data.get('fechaDesde') if data else None
    fecha_hasta = data.get('fechaHasta') if data else None
    totales = filtrar_ventas(fecha_desde, fecha_hasta)
    return jsonify(totales)

@finanzas_bp.route('/corteCaja')
@login_required 
@admin_required 
def corte():
    nombre_usuario = session['usuario']
    cortes = obtener_todos_cortes()
    return render_template('corteCaja.html', cortes=cortes, nombre_usuario=nombre_usuario)

@finanzas_bp.route('/api/corteCaja/<int:id>', methods=['GET'])
@login_required
def get_corte_caja(id):
    try:
        corte = obtener_corte_por_id(id)
        if corte:
            return jsonify({'success': True, 'corte': corte})
        else:
            return jsonify({'success': False, 'message': 'Corte de caja no encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@finanzas_bp.route('/guardarCorteCaja', methods=['POST'])
@login_required
def guardar_corte():
    try:
        data = request.get_json()

        vendedor_id = session.get('usuario_id')

        exito = guardar_corte_caja(
            vendedor_id,
            data.get('fecha_hora_inicio'),
            data.get('fecha_hora_cierre'),
            float(data.get('total_ventas', 0)),
            float(data.get('total_efectivo', 0)),
            float(data.get('total_transferencias', 0)),
            float(data.get('total_paypal', 0)),
            float(data.get('total_contado', 0)),
            float(data.get('pagos_realizados', 0)),
            float(data.get('fondo', 0))
        )

        if exito:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al guardar el corte"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500

@finanzas_bp.route('/reporteFinanciero')
@login_required
def reporte():
    cortes = obtener_cortes_con_ganancia()
    return render_template('reportesFinancieros.html', cortes=cortes)
