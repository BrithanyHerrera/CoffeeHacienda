from flask import Blueprint, render_template, request, jsonify
from bd import Conexion_BD
from utils import login_required, admin_required
from models.modelsInventario import obtener_productos_inventario, actualizar_stock_producto

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/inventario')
@login_required
@admin_required 
def inventario():
    # Obtener productos que requieren inventario
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
        
        # Validar que los valores no sean cero
        if nuevo_stock_min == 0:
            return jsonify({
                'success': False,
                'message': 'El stock mínimo no puede ser cero'
            })
            
        if nuevo_stock_max == 0:
            return jsonify({
                'success': False,
                'message': 'El stock máximo no puede ser cero'
            })
            
        # Validar que el stock mínimo y máximo no sean iguales
        if nuevo_stock_min == nuevo_stock_max:
            return jsonify({
                'success': False,
                'message': 'El stock mínimo y máximo no pueden ser iguales'
            })
        
        # Validar que el stock mínimo no sea mayor que el stock máximo
        if nuevo_stock_min > nuevo_stock_max:
            return jsonify({
                'success': False,
                'message': 'El stock mínimo no puede ser mayor que el stock máximo'
            })
            
        # Validar que el stock máximo no sea menor que el stock mínimo
        if nuevo_stock_max < nuevo_stock_min:
            return jsonify({
                'success': False,
                'message': 'El stock máximo no puede ser menor que el stock mínimo'
            })
        
        # Obtener valores actuales del producto directamente (sin cargar todos)
        conn_check = Conexion_BD()
        cursor_check = conn_check.cursor()
        cursor_check.execute("""
            SELECT p.Id, p.stock, p.stock_minimo, p.stock_maximo
            FROM tproductos p
            INNER JOIN tcategorias c ON p.categoria_id = c.Id
            WHERE p.Id = %s AND p.activo = 1 AND c.requiere_inventario = 1
        """, (id_producto,))
        producto_actual = cursor_check.fetchone()
        cursor_check.close()
        conn_check.close()

        if not producto_actual:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            })
        
        # Verificar si hay cambios
        if (producto_actual['stock'] == nuevo_stock and 
            producto_actual['stock_minimo'] == nuevo_stock_min and 
            producto_actual['stock_maximo'] == nuevo_stock_max):
            return jsonify({
                'success': True,
                'message': 'No se realizaron cambios en el inventario'
            })
        
        resultado = actualizar_stock_producto(id_producto, nuevo_stock, nuevo_stock_min, nuevo_stock_max)
        
        # Determinar mensaje basado en qué cambió
        mensaje = 'Inventario actualizado correctamente'
        if resultado:
            if producto_actual['stock'] != nuevo_stock and producto_actual['stock_minimo'] == nuevo_stock_min and producto_actual['stock_maximo'] == nuevo_stock_max:
                mensaje = 'Stock actualizado correctamente'
            elif producto_actual['stock'] == nuevo_stock and (producto_actual['stock_minimo'] != nuevo_stock_min or producto_actual['stock_maximo'] != nuevo_stock_max):
                mensaje = 'Límites de stock actualizados correctamente'
        else:
            mensaje = 'Error al actualizar inventario'
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
