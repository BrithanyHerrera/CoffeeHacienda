# Rutas: corte de caja y reportes
import os
from flask import Blueprint, render_template, request, jsonify, session, current_app
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

import os
from flask import Blueprint, jsonify, url_for, current_app

# Asumiendo que tu blueprint se define así
# finanzas_bp = Blueprint('finanzas', __name__)

@finanzas_bp.route('/buscar_pdf_corte/<fecha_inicio>/<fecha_fin>')
def buscar_pdf_corte(fecha_inicio, fecha_fin):
    # Usamos current_app.root_path para asegurar que la ruta sea absoluta y no falle
    directorio_pdfs = os.path.join(current_app.root_path, 'static', 'pdfs', 'cortes_de_caja')
    
    # Limpiamos caracteres que no pueden ir en nombres de archivos (como los ':' de las horas)
    # Esto es vital si tus archivos se guardan como "2026-05-11_08-00-00"
    f_inicio_limpia = fecha_inicio.replace(':', '-')
    f_fin_limpia = fecha_fin.replace(':', '-')

    try:
        if not os.path.exists(directorio_pdfs):
            return jsonify({'success': False, 'message': 'Carpeta de PDFs no encontrada'})

        archivos = os.listdir(directorio_pdfs)
        
        for archivo in archivos:
            # Buscamos que ambas fechas coincidan en el nombre del archivo
            if f_inicio_limpia in archivo and f_fin_limpia in archivo and archivo.endswith('.pdf'):
                return jsonify({
                    'success': True, 
                    'url': url_for('static', filename=f'pdfs/cortes_de_caja/{archivo}')
                })
        
        return jsonify({'success': False, 'message': f'No existe PDF del {fecha_inicio} al {fecha_fin}'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
