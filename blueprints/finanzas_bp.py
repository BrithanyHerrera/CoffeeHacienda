# Rutas: corte de caja y reportes
import os
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, jsonify, session, current_app, url_for
from utils import login_required, admin_required
from models.modelsCorteCaja import (filtrar_ventas, guardar_corte_caja, obtener_corte_por_id,
                                     obtener_todos_cortes, obtener_cortes_con_ganancia)

finanzas_bp = Blueprint('finanzas', __name__)
logger = logging.getLogger(__name__)


def _decimal_no_negativo(valor, nombre):
    try:
        numero = Decimal(str(valor)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f'{nombre} no es un importe válido')
    if numero < 0:
        raise ValueError(f'{nombre} no puede ser negativo')
    return numero


def _rango_fechas(data):
    inicio_texto = data.get('fecha_hora_inicio') or data.get('fechaDesde')
    cierre_texto = data.get('fecha_hora_cierre') or data.get('fechaHasta')
    if not inicio_texto or not cierre_texto:
        raise ValueError('Selecciona las fechas de inicio y cierre')
    try:
        inicio = datetime.fromisoformat(inicio_texto)
        cierre = datetime.fromisoformat(cierre_texto)
    except (TypeError, ValueError):
        raise ValueError('El rango de fechas no es válido')
    if inicio >= cierre:
        raise ValueError('La fecha de inicio debe ser anterior a la fecha de cierre')
    return inicio, cierre

@finanzas_bp.route('/filtrarVentas', methods=['POST'])
@login_required
@admin_required
def filtrar_ventas_route():
    try:
        data = request.get_json(silent=True) or {}
        fecha_desde, fecha_hasta = _rango_fechas(data)
        totales = filtrar_ventas(fecha_desde, fecha_hasta)
        return jsonify(totales)
    except ValueError as error:
        return jsonify({'success': False, 'message': str(error)}), 400

@finanzas_bp.route('/corteCaja')
@login_required 
@admin_required 
def corte():
    nombre_usuario = session['usuario']
    cortes = obtener_todos_cortes()
    return render_template('corteCaja.html', cortes=cortes, nombre_usuario=nombre_usuario)

@finanzas_bp.route('/api/corteCaja/<int:id>', methods=['GET'])
@login_required
@admin_required
def get_corte_caja(id):
    try:
        corte = obtener_corte_por_id(id)
        if corte:
            return jsonify({'success': True, 'corte': corte})
        else:
            return jsonify({'success': False, 'message': 'Corte de caja no encontrado'})
    except Exception:
        logger.exception('Error al obtener corte de caja')
        return jsonify({'success': False, 'message': 'No se pudo obtener el corte de caja'}), 500

@finanzas_bp.route('/guardarCorteCaja', methods=['POST'])
@login_required
@admin_required
def guardar_corte():
    try:
        data = request.get_json(silent=True) or {}
        fecha_inicio, fecha_cierre = _rango_fechas(data)
        vendedor_id = session.get('usuario_id')
        if not vendedor_id:
            return jsonify({'success': False, 'error': 'La sesión no tiene un usuario válido'}), 401

        totales = filtrar_ventas(fecha_inicio, fecha_cierre)
        total_ventas = sum(totales.values(), Decimal('0.00'))
        total_contado = _decimal_no_negativo(data.get('total_contado', 0), 'Total contado')
        pagos_realizados = _decimal_no_negativo(data.get('pagos_realizados', 0), 'Pagos realizados')
        fondo = _decimal_no_negativo(data.get('fondo', 0), 'Fondo')

        if abs(total_contado - total_ventas) > Decimal('0.01'):
            return jsonify({
                'success': False,
                'error': 'El total contado no coincide con las ventas calculadas por el servidor',
            }), 409

        if pagos_realizados > total_ventas + fondo:
            return jsonify({
                'success': False,
                'error': 'Los pagos realizados superan el total disponible',
            }), 400

        exito, mensaje, corte_id = guardar_corte_caja(
            vendedor_id,
            fecha_inicio,
            fecha_cierre,
            total_ventas,
            totales['efectivo'],
            totales['transferencias'],
            totales['tarjeta'],
            total_contado,
            pagos_realizados,
            fondo,
        )

        if exito:
            return jsonify({'success': True, 'corte_id': corte_id})
        else:
            return jsonify({'success': False, 'error': mensaje}), 409

    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    except Exception:
        logger.exception('Error al guardar corte de caja')
        return jsonify({'success': False, 'error': 'No se pudo guardar el corte'}), 500

@finanzas_bp.route('/reporteFinanciero')
@login_required
@admin_required
def reporte():
    cortes = obtener_cortes_con_ganancia()
    return render_template('reportesFinancieros.html', cortes=cortes)

@finanzas_bp.route('/buscar_pdf_corte/<fecha_inicio>/<fecha_fin>')
@login_required
@admin_required
def buscar_pdf_corte(fecha_inicio, fecha_fin):
    # Usamos current_app.root_path para asegurar que la ruta sea absoluta y no falle
    directorio_pdfs = current_app.config['PDF_CORTES_FOLDER']
    
    # Limpiamos caracteres que no pueden ir en nombres de archivos (como los ':' de las horas)
    # Esto es vital si tus archivos se guardan como "2026-05-11_08-00-00"
    f_inicio_limpia = fecha_inicio[:10]
    f_fin_limpia = fecha_fin[:10]

    try:
        if not os.path.exists(directorio_pdfs):
            return jsonify({'success': False, 'message': 'Carpeta de PDFs no encontrada'})

        archivos = sorted(os.listdir(directorio_pdfs), reverse=True)
        
        for archivo in archivos:
            # Buscamos que ambas fechas coincidan en el nombre del archivo
            if f_inicio_limpia in archivo and f_fin_limpia in archivo and archivo.endswith('.pdf'):
                return jsonify({
                    'success': True, 
                    'url': url_for('core.descargar_pdf', tipo='corte', nombre=archivo)
                })
        
        return jsonify({'success': False, 'message': f'No existe PDF del {fecha_inicio} al {fecha_fin}'})
    
    except Exception:
        logger.exception('Error al buscar PDF de corte')
        return jsonify({'success': False, 'message': 'No se pudo buscar el PDF'}), 500
