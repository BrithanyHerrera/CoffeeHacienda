# Rutas de inventario — consulta y actualización de stock
from flask import Blueprint, render_template, request, jsonify
from utils import login_required, admin_required
from models.modelsInventario import (obtener_productos_inventario, actualizar_stock_producto,
                                      obtener_producto_inventario_por_id)

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/inventario')
@login_required
@admin_required 
def inventario():
    productos = obtener_productos_inventario()
    return render_template('inventario.html', productos=productos)

@inventario_bp.route('/api/inventario/actualizar', methods=['POST'])
@login_required
@admin_required
def actualizar_inventario():
    try:
        data = request.json
        id_producto = data.get('id')
        nuevo_stock = data.get('stock')
        nuevo_stock_min = data.get('stock_min')
        nuevo_stock_max = data.get('stock_max')
        
        if nuevo_stock_min == 0:
            return jsonify({'success': False, 'message': 'El stock mínimo no puede ser cero'})
            
        if nuevo_stock_max == 0:
            return jsonify({'success': False, 'message': 'El stock máximo no puede ser cero'})
            
        if nuevo_stock_min == nuevo_stock_max:
            return jsonify({'success': False, 'message': 'El stock mínimo y máximo no pueden ser iguales'})
        
        if nuevo_stock_min > nuevo_stock_max:
            return jsonify({'success': False, 'message': 'El stock mínimo no puede ser mayor que el stock máximo'})
        
        producto_actual = obtener_producto_inventario_por_id(id_producto)

        if not producto_actual:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        # Si nada cambió, no hacer update
        if (producto_actual['stock'] == nuevo_stock and 
            producto_actual['stock_minimo'] == nuevo_stock_min and 
            producto_actual['stock_maximo'] == nuevo_stock_max):
            return jsonify({'success': True, 'message': 'No se realizaron cambios en el inventario'})
        
        resultado = actualizar_stock_producto(id_producto, nuevo_stock, nuevo_stock_min, nuevo_stock_max)
        
        mensaje = 'Inventario actualizado correctamente'
        if resultado:
            if producto_actual['stock'] != nuevo_stock and producto_actual['stock_minimo'] == nuevo_stock_min and producto_actual['stock_maximo'] == nuevo_stock_max:
                mensaje = 'Stock actualizado correctamente'
            elif producto_actual['stock'] == nuevo_stock and (producto_actual['stock_minimo'] != nuevo_stock_min or producto_actual['stock_maximo'] != nuevo_stock_max):
                mensaje = 'Límites de stock actualizados correctamente'
        else:
            mensaje = 'Error al actualizar inventario'
        
        return jsonify({'success': resultado, 'message': mensaje})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
