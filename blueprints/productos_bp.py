# Rutas: productos, imágenes y variantes
import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import secrets
import time
from utils import login_required, admin_required, archivo_permitido
from models.modelsProductos import (obtener_productos, obtener_categorias, obtener_tamanos,
                                agregar_producto, actualizar_producto, eliminar_producto,
                                obtener_producto_por_id, agregar_variante_producto,
                                obtener_variantes_por_producto,
                                eliminar_variantes_producto, obtener_variantes_batch)

productos_bp = Blueprint('productos', __name__)
logger = logging.getLogger(__name__)


def _firma_imagen_valida(archivo, extension):
    encabezado = archivo.stream.read(12)
    archivo.stream.seek(0)
    firmas = {
        'png': encabezado.startswith(b'\x89PNG\r\n\x1a\n'),
        'jpg': encabezado.startswith(b'\xff\xd8\xff'),
        'jpeg': encabezado.startswith(b'\xff\xd8\xff'),
        'gif': encabezado.startswith((b'GIF87a', b'GIF89a')),
    }
    return firmas.get(extension, False)

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
    except Exception:
        logger.exception('Error al obtener categorías')
        return jsonify({'success': False, 'message': 'No se pudieron cargar las categorías'}), 500

@productos_bp.route('/api/tamanos', methods=['GET'])
@login_required
def get_tamanos():
    try:
        return jsonify({'success': True, 'tamanos': obtener_tamanos()})
    except Exception:
        logger.exception('Error al obtener tamaños')
        return jsonify({'success': False, 'message': 'No se pudieron cargar los tamaños'}), 500

@productos_bp.route('/api/productos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_producto():
    try:
        id_producto = request.form.get('id')
        nombre = (request.form.get('nombreProducto') or '').strip()
        descripcion = (request.form.get('descripcionProducto') or '').strip()
        precio = float(request.form.get('precioProducto'))
        stock = int(request.form.get('stockProducto') or 0)
        stock_min = int(request.form.get('stockMinProducto') or 0)
        stock_max = int(request.form.get('stockMaxProducto') or 0)
        categoria_id = int(request.form.get('categoriaProducto'))
        tamano_id = int(request.form.get('tamano_id'))

        if not nombre or len(nombre) > 255:
            return jsonify({'success': False, 'message': 'El nombre del producto no es válido'}), 400
        if len(descripcion) > 2000:
            return jsonify({'success': False, 'message': 'La descripción es demasiado larga'}), 400
        if precio < 0 or stock < 0 or stock_min < 0 or stock_max < 0:
            return jsonify({'success': False, 'message': 'Precio y existencias no pueden ser negativos'}), 400
        if stock_min > stock_max:
            return jsonify({'success': False, 'message': 'El stock mínimo no puede superar al máximo'}), 400

        ruta_imagen = None
        if 'imagenProducto' in request.files:
            archivo = request.files['imagenProducto']
            if archivo and archivo.filename:
                if not archivo_permitido(archivo.filename):
                    return jsonify({'success': False, 'message': 'Formato de imagen no permitido'}), 400
                extension = archivo.filename.rsplit('.', 1)[1].lower()
                if not _firma_imagen_valida(archivo, extension):
                    return jsonify({'success': False, 'message': 'El contenido no corresponde a una imagen válida'}), 400
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = secure_filename(f'{timestamp}_{secrets.token_hex(4)}.{extension}')
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
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
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Los datos del producto no son válidos'}), 400
    except Exception:
        logger.exception('Error en guardar_producto')
        return jsonify({'success': False, 'message': 'No se pudo guardar el producto'}), 500

@productos_bp.route('/api/productos/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_producto_route():
    try:
        data = request.get_json(silent=True) or {}
        id_producto = data.get('id')
        resultado = eliminar_producto(id_producto)
        return jsonify({'success': resultado, 'message': 'Producto eliminado' if resultado else 'Error al eliminar'})
    except Exception:
        logger.exception('Error al desactivar producto')
        return jsonify({'success': False, 'message': 'No se pudo desactivar el producto'}), 500

@productos_bp.route('/api/productos/variantes', methods=['POST'])
@login_required
@admin_required
def guardar_variante():
    try:
        data = request.get_json(silent=True) or {}
        producto_id = int(data.get('producto_id'))
        tamano_id = int(data.get('tamano_id'))
        precio = float(data.get('precio'))
        if producto_id <= 0 or tamano_id <= 0 or precio < 0:
            raise ValueError
        resultado = agregar_variante_producto(producto_id, tamano_id, precio)
        return jsonify({'success': resultado, 'message': 'Variante agregada' if resultado else 'Error al agregar'})
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Los datos de la variante no son válidos'}), 400
    except Exception:
        logger.exception('Error al guardar variante')
        return jsonify({'success': False, 'message': 'No se pudo guardar la variante'}), 500

@productos_bp.route('/api/productos/variantes/<int:producto_id>', methods=['GET'])
@login_required
def obtener_variantes(producto_id):
    try:
        return jsonify({'success': True, 'variantes': obtener_variantes_por_producto(producto_id)})
    except Exception:
        logger.exception('Error al obtener variantes')
        return jsonify({'success': False, 'message': 'No se pudieron cargar las variantes'}), 500

@productos_bp.route('/api/productos/<int:id>', methods=['GET'])
@login_required
def get_producto(id):
    try:
        producto = obtener_producto_por_id(id)
        if producto:
            variantes = obtener_variantes_por_producto(id)
            return jsonify({'success': True, 'producto': producto, 'variantes': variantes})
        return jsonify({'success': False, 'message': 'Producto no encontrado'})
    except Exception:
        logger.exception('Error al obtener producto')
        return jsonify({'success': False, 'message': 'No se pudo cargar el producto'}), 500

@productos_bp.route('/api/categorias/<int:id>', methods=['GET'])
@login_required
def get_categoria(id):
    try:
        categorias = obtener_categorias()
        categoria = next((cat for cat in categorias if cat['Id'] == id), None)
        if categoria:
            return jsonify({'success': True, 'categoria': categoria})
        return jsonify({'success': False, 'message': 'Categoría no encontrada'})
    except Exception:
        logger.exception('Error al obtener categoría')
        return jsonify({'success': False, 'message': 'No se pudo cargar la categoría'}), 500
