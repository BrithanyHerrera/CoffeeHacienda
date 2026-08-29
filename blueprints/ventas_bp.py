# Rutas: menú, órdenes, historial y ventas
import logging
from flask import Blueprint, render_template, request, jsonify, session
from utils import login_required
from models.modelsProductosMenu import obtener_metodos_pago, obtener_productos_menu
from models.modelsVentas import (obtener_ordenes_pendientes, actualizar_estado_orden,
                                obtener_detalle_orden, obtener_estado_orden,
                                cancelar_orden, obtener_vendedores_activos,
                                obtener_venta_completa, procesar_venta_completa)
from models.modelsHistorial import obtener_historial_ventas

ventas_bp = Blueprint('ventas', __name__)

logger = logging.getLogger(__name__)

@ventas_bp.route('/menu')
@login_required
def menu():
    nombre_usuario = session['usuario']
    productos = obtener_productos_menu()
    metodos_pago = obtener_metodos_pago()
    return render_template(
        'menu.html',
        nombre_usuario=nombre_usuario,
        productos=productos,
        metodos_pago=metodos_pago,
    )

@ventas_bp.route('/ordenes')
@login_required
def ordenes():
    ordenes_pendientes = obtener_ordenes_pendientes()
    vendedores = obtener_vendedores_activos()
    return render_template('ordenes.html', ordenes=ordenes_pendientes, vendedores=vendedores)

@ventas_bp.route('/api/ordenes', methods=['GET'])
@login_required
def api_obtener_ordenes():
    try:
        ordenes = obtener_ordenes_pendientes()
        return jsonify({'success': True, 'ordenes': ordenes})
    except Exception as e:
        logger.error("Error al obtener órdenes pendientes: %s", e)
        return jsonify({'success': False, 'message': 'No se pudieron cargar las órdenes'}), 500

@ventas_bp.route('/api/ordenes/<int:id>/detalles', methods=['GET'])
@login_required
def api_detalle_orden(id):
    try:
        detalles = obtener_detalle_orden(id)
        if detalles:
            return jsonify({'success': True, 'detalles': detalles})
        else:
            return jsonify({'success': False, 'message': 'Orden no encontrada'})
    except Exception as e:
        logger.error("Error al obtener detalle de orden: %s", e)
        return jsonify({'success': False, 'message': 'No se pudo cargar el detalle'}), 500

@ventas_bp.route('/api/ordenes/<int:id>/estado', methods=['POST'])
@login_required
def api_actualizar_estado_orden(id):
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Solicitud JSON no válida'}), 400
        nuevo_estado = data.get('estado')
        
        estados = {
            'Pendiente': 1,
            'En proceso': 2,
            'Cancelado': 3,
            'Completado': 4,
            'Reembolsada': 5
        }
        
        if nuevo_estado not in estados:
            return jsonify({'success': False, 'message': 'Estado no válido'}), 400
        
        resultado = obtener_estado_orden(id)
        
        if not resultado:
            return jsonify({'success': False, 'message': 'Orden no encontrada'}), 404
        
        estado_actual_id = resultado['estado_id']
        
        # Transiciones permitidas entre estados
        transiciones_validas = {
            1: [2, 3],     # Pendiente -> En proceso, Cancelado
            2: [3, 4],     # En proceso -> Cancelado, Completado
            3: [],         # Cancelado (final)
            4: [],         # Completado (final)
            5: []          # Reembolsada (final)
        }
        
        transiciones_desde_estado = transiciones_validas.get(estado_actual_id, [])
        if estados[nuevo_estado] not in transiciones_desde_estado and estados[nuevo_estado] != estado_actual_id:
            estado_actual_nombre = next((nombre for nombre, id in estados.items() if id == estado_actual_id), "Desconocido")
            estados_validos = [next((nombre for nombre, id in estados.items() if id == estado_id), "Desconocido") 
                            for estado_id in transiciones_desde_estado]
            mensaje_estados = ", ".join(estados_validos) if estados_validos else "ninguno"
            
            return jsonify({
                'success': False,
                'message': f'Transición no válida. Desde "{estado_actual_nombre}" solo puede cambiar a: {mensaje_estados}'
            })
        
        if nuevo_estado == 'Cancelado':
            motivo_cancelacion = str(data.get('motivo') or '').strip()
            if len(motivo_cancelacion) < 3 or len(motivo_cancelacion) > 255:
                return jsonify({
                    'success': False,
                    'message': 'Indica un motivo de cancelación entre 3 y 255 caracteres'
                }), 400

            if cancelar_orden(id, session.get('usuario_id'), motivo_cancelacion):
                return jsonify({
                    'success': True,
                    'message': 'Orden cancelada; el inventario correspondiente fue repuesto'
                })
            return jsonify({
                'success': False,
                'message': 'No fue posible cancelar la orden en su estado actual'
            }), 409
        else:
            resultado = actualizar_estado_orden(id, estados[nuevo_estado])
            if resultado:
                return jsonify({'success': True, 'message': f'Estado actualizado a {nuevo_estado}'})
            else:
                return jsonify({'success': False, 'message': 'No fue posible actualizar el estado'}), 409
    except Exception as e:
        logger.error(f"Error al actualizar estado de orden: {e}")
        return jsonify({'success': False, 'message': 'No fue posible actualizar el estado'}), 500

@ventas_bp.route('/historial')
@login_required
def historial():
    vendedores = obtener_vendedores_activos()
    return render_template('historial.html', vendedores=vendedores)

@ventas_bp.route('/api/historial-ventas', methods=['GET'])
@login_required
def api_historial_ventas():
    filtro_cliente = request.args.get('cliente', '')
    filtro_vendedor = request.args.get('vendedor', '')
    fecha_inicio = request.args.get('fechaInicio', '')
    fecha_fin = request.args.get('fechaFin', '')
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = request.args.get('por_pagina', 15, type=int)

    try:
        ventas, total_paginas, total = obtener_historial_ventas(
            filtro_cliente, filtro_vendedor, fecha_inicio, fecha_fin, pagina, por_pagina)
        return jsonify({
            'success': True, 
            'ventas': ventas,
            'pagina_actual': pagina,
            'total_paginas': total_paginas,
            'total_ventas': total
        })
    except Exception as e:
        logger.error("Error al consultar historial de ventas: %s", e)
        return jsonify({'success': False, 'message': 'No se pudo cargar el historial'}), 500

@ventas_bp.route('/api/historial-ventas/<int:id>', methods=['GET'])
@login_required
def api_detalle_venta(id):
    try:
        venta, detalles = obtener_venta_completa(id)
        if not venta:
            return jsonify({'success': False, 'message': 'Venta no encontrada'})
        return jsonify({'success': True, 'venta': venta, 'detalles': detalles})
    except Exception as e:
        logger.error("Error al obtener detalles de venta: %s", e)
        return jsonify({'success': False, 'message': 'No se pudo cargar el detalle de la venta'}), 500

@ventas_bp.route('/api/ventas/crear', methods=['POST'])
@login_required
def procesar_venta():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Solicitud JSON no válida'}), 400
        
        nombre_cliente = data.get('cliente', 'Cliente General')
        numero_mesa = data.get('mesa', '')
        productos = data.get('productos', [])
        metodo_pago_id = data.get('metodo_pago')
        dinero_recibido = data.get('dinero_recibido', 0)
        usuario_actual = session.get('usuario', '')
        
        if not productos:
            return jsonify({'success': False, 'message': 'No se proporcionaron productos'})
        
        exito, mensaje, datos = procesar_venta_completa(
            nombre_cliente, numero_mesa, productos, None, metodo_pago_id,
            usuario_actual, dinero_recibido, None
        )
        
        if exito:
            return jsonify({'success': True, 'message': mensaje, **datos})
        else:
            response = {'success': False, 'message': mensaje}
            if datos and 'productos_sin_stock' in datos:
                response['productos_sin_stock'] = datos['productos_sin_stock']
            return jsonify(response), 400
            
    except Exception as e:
        logger.error("Error al procesar venta: %s", e)
        return jsonify({'success': False, 'message': 'No fue posible registrar la venta'}), 500
