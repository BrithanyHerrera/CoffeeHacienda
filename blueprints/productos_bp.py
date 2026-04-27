# Rutas de gestión de productos — CRUD, imágenes, variantes y categorías
import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os, time
from utils import login_required, admin_required, archivo_permitido
from models.modelsProductos import (obtener_productos, obtener_categorias, obtener_tamanos,
                                agregar_producto, actualizar_producto, eliminar_producto,
                                obtener_producto_por_id, agregar_variante_producto,
                                obtener_variantes_por_producto, actualizar_variante_producto,
                                eliminar_variantes_producto, obtener_variantes_batch)

productos_bp = Blueprint('productos', __name__)
logger = logging.getLogger(__name__)

@productos_bp.route('/gestionProductos')
@login_required
@admin_required
def gestion_productos():
    productos = obtener_productos()
    if productos:
        producto_ids = [p['Id'] for p in productos]
        variantes_por_producto = obtener_variantes_batch(producto_ids)
        for producto in productos:
            producto['variantes'] = variantes_por_producto.get(producto['Id'], [])
    categorias = obtener_categorias()
    tamanos = obtener_tamanos()
    return render_template('gestionProductos.html', productos=productos, categorias=categorias, tamanos=tamanos)

@productos_bp.route('/api/categorias', methods=['GET'])
@login_required
def get_categorias():
    try:
        return jsonify({'success': True, 'categorias': obtener_categorias()})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/tamanos', methods=['GET'])
@login_required
def get_tamanos():
    try:
        return jsonify({'success': True, 'tamanos': obtener_tamanos()})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/productos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_producto():
    try:
        id_producto = request.form.get('id')
        nombre = request.form.get('nombreProducto')
        descripcion = request.form.get('descripcionProducto')
        precio = float(request.form.get('precioProducto'))
        stock = int(request.form.get('stockProducto') or 0)
        stock_min = int(request.form.get('stockMinProducto') or 0)
        stock_max = int(request.form.get('stockMaxProducto') or 0)
        categoria_id = int(request.form.get('categoriaProducto'))
        tamano_id = int(request.form.get('tamano_id'))
        ruta_imagen = None
        if 'imagenProducto' in request.files:
            archivo = request.files['imagenProducto']
            if archivo and archivo.filename and archivo_permitido(archivo.filename):
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = secure_filename(timestamp + '.' + archivo.filename.rsplit('.', 1)[1].lower())
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                archivo.save(os.path.join(upload_folder, filename))
                ruta_imagen = f'/static/images/productos/{filename}'
        if id_producto:
            producto_actual = obtener_producto_por_id(id_producto)
            if not ruta_imagen and producto_actual and producto_actual.get('ruta_imagen'):
                ruta_imagen = producto_actual['ruta_imagen']
            resultado, mensaje = actualizar_producto(id_producto, nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen)
            if tamano_id and tamano_id != 4:
                eliminar_variantes_producto(id_producto)
                agregar_variante_producto(id_producto, tamano_id, precio)
            elif tamano_id == 4:
                eliminar_variantes_producto(id_producto)
        else:
            resultado, nuevo_id = agregar_producto(nombre, descripcion, precio, stock, stock_min, stock_max, categoria_id, ruta_imagen)
            if resultado and tamano_id and tamano_id != 4:
                agregar_variante_producto(nuevo_id, tamano_id, precio)
            mensaje = 'Producto creado exitosamente' if resultado else 'Error al crear producto'
        return jsonify({'success': resultado, 'message': mensaje})
    except Exception as e:
        logger.error(f"Error en guardar_producto: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/productos/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_producto_route():
    try:
        data = request.json
        id_producto = data.get('id')
        eliminar_variantes_producto(id_producto)
        resultado = eliminar_producto(id_producto)
        return jsonify({'success': resultado, 'message': 'Producto eliminado' if resultado else 'Error al eliminar'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/productos/variantes', methods=['POST'])
@login_required
def guardar_variante():
    try:
        data = request.json
        resultado = agregar_variante_producto(data.get('producto_id'), data.get('tamano_id'), data.get('precio'))
        return jsonify({'success': resultado, 'message': 'Variante agregada' if resultado else 'Error al agregar'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/productos/variantes/<int:producto_id>', methods=['GET'])
@login_required
def obtener_variantes(producto_id):
    try:
        return jsonify({'success': True, 'variantes': obtener_variantes_por_producto(producto_id)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/productos/<int:id>', methods=['GET'])
@login_required
def get_producto(id):
    try:
        producto = obtener_producto_por_id(id)
        if producto:
            variantes = obtener_variantes_por_producto(id)
            return jsonify({'success': True, 'producto': producto, 'variantes': variantes})
        return jsonify({'success': False, 'message': 'Producto no encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@productos_bp.route('/api/categorias/<int:id>', methods=['GET'])
@login_required
def get_categoria(id):
    try:
        categorias = obtener_categorias()
        categoria = next((cat for cat in categorias if cat['Id'] == id), None)
        if categoria:
            return jsonify({'success': True, 'categoria': categoria})
        return jsonify({'success': False, 'message': 'Categoría no encontrada'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
