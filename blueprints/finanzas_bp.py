# Rutas: corte de caja y reportes
import csv
import io
import os
import re
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, jsonify, session, current_app, url_for, send_file
from utils import login_required, admin_required
from models.modelsCorteCaja import (
    filtrar_ventas,
    guardar_corte_caja,
    obtener_corte_por_id,
    obtener_todos_cortes,
    obtener_cortes_con_ganancia,
    obtener_ultimo_corte,
    obtener_fecha_sugerida_inicio,
)

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
        totales_serializables = {k: float(v) if isinstance(v, Decimal) else v for k, v in totales.items()}
        return jsonify(totales_serializables)
    except ValueError as error:
        return jsonify({'success': False, 'message': str(error)}), 400


@finanzas_bp.route('/corteCaja')
@login_required 
@admin_required 
def corte():
    nombre_usuario = session['usuario']
    cortes = obtener_todos_cortes()
    fecha_sugerida_dt, tiene_corte_previo = obtener_fecha_sugerida_inicio()

    fecha_inicio_sugerida = ''
    if fecha_sugerida_dt:
        if isinstance(fecha_sugerida_dt, str):
            try:
                fecha_sugerida_dt = datetime.fromisoformat(fecha_sugerida_dt)
            except Exception:
                fecha_sugerida_dt = None
        if fecha_sugerida_dt:
            fecha_inicio_sugerida = fecha_sugerida_dt.strftime('%Y-%m-%dT%H:%M')

    return render_template(
        'corteCaja.html',
        cortes=cortes,
        nombre_usuario=nombre_usuario,
        fecha_inicio_sugerida=fecha_inicio_sugerida,
        tiene_corte_previo=tiene_corte_previo,
    )


@finanzas_bp.route('/api/corteCaja/ultimo', methods=['GET'])
@login_required
@admin_required
def get_ultimo_corte():
    try:
        ultimo = obtener_ultimo_corte()
        fecha_sugerida_dt, tiene_corte_previo = obtener_fecha_sugerida_inicio()
        fecha_iso = ''
        if fecha_sugerida_dt:
            if isinstance(fecha_sugerida_dt, str):
                try:
                    fecha_sugerida_dt = datetime.fromisoformat(fecha_sugerida_dt)
                except Exception:
                    fecha_sugerida_dt = None
            if fecha_sugerida_dt:
                fecha_iso = fecha_sugerida_dt.strftime('%Y-%m-%dT%H:%M')
        return jsonify({
            'success': True,
            'ultimo_corte': ultimo,
            'fecha_inicio_sugerida': fecha_iso,
            'tiene_corte_previo': tiene_corte_previo,
        })
    except Exception:
        logger.exception('Error al obtener fecha de último corte')
        return jsonify({'success': False, 'message': 'No se pudo obtener el último corte'}), 500


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
            return jsonify({'success': False, 'message': 'La sesión no tiene un usuario válido', 'error': 'La sesión no tiene un usuario válido'}), 401

        # Validar continuidad con el último corte registrado si existe
        ultimo_corte = obtener_ultimo_corte()
        if ultimo_corte and ultimo_corte.get('fecha_hora_cierre'):
            ultimo_cierre = ultimo_corte['fecha_hora_cierre']
            if isinstance(ultimo_cierre, str):
                try:
                    ultimo_cierre = datetime.fromisoformat(ultimo_cierre)
                except Exception:
                    ultimo_cierre = None
            if ultimo_cierre:
                # Tolerancia de 60 segundos por diferencias de formato en inputs datetime-local
                diferencia_segundos = abs((fecha_inicio - ultimo_cierre).total_seconds())
                if diferencia_segundos > 60:
                    mensaje_discontinuidad = (
                        f'El corte debe iniciar exactamente al cierre del último corte registrado '
                        f'({ultimo_cierre.strftime("%Y-%m-%d %H:%M")})'
                    )
                    return jsonify({
                        'success': False,
                        'message': mensaje_discontinuidad,
                        'error': mensaje_discontinuidad,
                    }), 400

        totales = filtrar_ventas(fecha_inicio, fecha_cierre)
        total_ventas = sum(totales.values(), Decimal('0.00'))
        total_contado = _decimal_no_negativo(data.get('total_contado', 0), 'Total contado')
        pagos_realizados = _decimal_no_negativo(data.get('pagos_realizados', 0), 'Pagos realizados')
        fondo = _decimal_no_negativo(data.get('fondo', 0), 'Fondo')

        if abs(total_contado - total_ventas) > Decimal('0.01'):
            return jsonify({
                'success': False,
                'message': 'El total contado no coincide con las ventas calculadas por el servidor',
                'error': 'El total contado no coincide con las ventas calculadas por el servidor',
            }), 409

        if pagos_realizados > total_ventas + fondo:
            return jsonify({
                'success': False,
                'message': 'Los pagos realizados superan el total disponible',
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
            return jsonify({'success': False, 'message': mensaje, 'error': mensaje}), 409

    except ValueError as error:
        return jsonify({'success': False, 'message': str(error), 'error': str(error)}), 400
    except Exception:
        logger.exception('Error al guardar corte de caja')
        return jsonify({'success': False, 'message': 'No se pudo guardar el corte', 'error': 'No se pudo guardar el corte'}), 500


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
    if not (re.match(r'^\d{4}-\d{2}-\d{2}$', f_inicio_limpia) and re.match(r'^\d{4}-\d{2}-\d{2}$', f_fin_limpia)):
        return jsonify({'success': False, 'message': 'Formato de fecha inválido'}), 400

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


def _formato_fecha_csv(val):
    """Convierte un valor de fecha/datetime a string para CSV."""
    if not val:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    return str(val)


def _formato_moneda_csv(val):
    """Convierte un valor monetario a string formateado con 2 decimales."""
    if val is None:
        return '0.00'
    try:
        return f"{Decimal(str(val)):.2f}"
    except (InvalidOperation, TypeError, ValueError):
        return '0.00'


def obtener_cortes_exportacion(fecha_desde=None, fecha_hasta=None):
    """Consulta todos los cortes con el nombre del vendedor para exportación."""
    from bd import Conexion_BD
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT c.Id, c.fecha_hora_inicio, c.fecha_hora_cierre,
                       COALESCE(u.usuario, 'N/A') AS vendedor,
                       c.total_ventas, c.total_efectivo, c.total_transferencias, c.total_tarjeta,
                       c.total_contado, c.pagos_realizados, c.fondo, c.ganancia_o_perdida
                FROM tcortescaja c
                LEFT JOIN tusuarios u ON c.vendedor_id = u.Id
            """
            params = []
            if fecha_desde and fecha_hasta:
                query += " WHERE c.fecha_hora_cierre >= %s AND c.fecha_hora_cierre <= %s"
                params.extend([fecha_desde, fecha_hasta])
            query += " ORDER BY c.fecha_hora_cierre DESC"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
    finally:
        conn.close()


@finanzas_bp.route('/api/cortes/exportar-excel', methods=['GET'])
@finanzas_bp.route('/exportarReporteFinancieroExcel', methods=['GET'])
@login_required
@admin_required
def exportar_cortes_excel():
    """Genera y descarga el reporte de cortes de caja en CSV/Excel compatible."""
    try:
        fecha_desde = request.args.get('fecha_desde') or request.args.get('fechaDesde')
        fecha_hasta = request.args.get('fecha_hasta') or request.args.get('fechaHasta')
        if fecha_desde and fecha_hasta:
            try:
                datetime.fromisoformat(fecha_desde)
                datetime.fromisoformat(fecha_hasta)
            except (ValueError, TypeError):
                fecha_desde = None
                fecha_hasta = None
        else:
            fecha_desde = None
            fecha_hasta = None

        cortes = obtener_cortes_exportacion(fecha_desde, fecha_hasta)

        si = io.StringIO()
        writer = csv.writer(si, lineterminator='\r\n')
        writer.writerow([
            'ID',
            'Fecha Inicio',
            'Fecha Cierre',
            'Vendedor',
            'Total Ventas',
            'Efectivo',
            'Transferencias',
            'Tarjeta',
            'Total Contado',
            'Pagos Realizados',
            'Fondo',
            'Ganancia/Pérdida',
        ])

        for c in cortes:
            writer.writerow([
                c.get('Id') if c.get('Id') is not None else c.get('id', ''),
                _formato_fecha_csv(c.get('fecha_hora_inicio')),
                _formato_fecha_csv(c.get('fecha_hora_cierre')),
                c.get('vendedor') or c.get('nombre_vendedor') or 'N/A',
                _formato_moneda_csv(c.get('total_ventas')),
                _formato_moneda_csv(c.get('total_efectivo')),
                _formato_moneda_csv(c.get('total_transferencias')),
                _formato_moneda_csv(c.get('total_tarjeta')),
                _formato_moneda_csv(c.get('total_contado')),
                _formato_moneda_csv(c.get('pagos_realizados')),
                _formato_moneda_csv(c.get('fondo')),
                _formato_moneda_csv(c.get('ganancia_o_perdida')),
            ])

        csv_bytes = io.BytesIO(si.getvalue().encode('utf-8-sig'))
        csv_bytes.seek(0)
        hoy = datetime.now().strftime('%Y%m%d')
        filename = f'Reporte_Cortes_Caja_{hoy}.csv'

        return send_file(
            csv_bytes,
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=filename,
        )
    except Exception:
        logger.exception('Error al exportar reporte de cortes de caja')
        return jsonify({'success': False, 'message': 'No se pudo generar la exportación'}), 500

