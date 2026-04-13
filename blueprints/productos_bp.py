from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import time
from utils import login_required, admin_required, allowed_file
from models.modelsProductos import (obtener_productos, obtener_categorias, obtener_tamanos,
                                agregar_producto, actualizar_producto, eliminar_producto,
                                obtener_producto_por_id, agregar_variante_producto,
                                obtener_variantes_por_producto, actualizar_variante_producto,
                                eliminar_variantes_producto)

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/gestionProductos')
@login_required
@admin_required
def gestion_productos():
    productos = obtener_productos()
    
    # Obtener TODAS las variantes en una sola consulta (en vez de N consultas)
    if productos:
        from bd import Conexion_BD
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        producto_ids = [p['Id'] for p in productos]
        placeholders = ', '.join(['%s'] * len(producto_ids))
        cursor.execute(f"""
            SELECT pv.*, t.tamano 
            FROM tproductos_variantes pv 
            JOIN ttamanos t ON pv.tamano_id = t.Id
            WHERE pv.producto_id IN ({placeholders})
            ORDER BY t.Id
        """, producto_ids)
        todas_variantes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Agrupar por producto
        variantes_por_producto = {}
        for v in todas_variantes:
            pid = v['producto_id']
            if pid not in variantes_por_producto:
                variantes_por_producto[pid] = []
            variantes_por_producto[pid].append(v)
        
        for producto in productos:
            producto['variantes'] = variantes_por_producto.get(producto['Id'], [])
    
    categorias = obtener_categorias()
    tamanos = obtener_tamanos()
    
    return render_template('gestionProductos.html', 
                        productos=productos,
                        categorias=categorias,
                        tamanos=tamanos)

@productos_bp.route('/api/categorias', methods=['GET'])
@login_required
def get_categorias():
    try:
        categorias = obtener_categorias()
        return jsonify({
            'success': True,
            'categorias': categorias
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/tamanos', methods=['GET'])
@login_required
def get_tamanos():
    try:
        tamanos = obtener_tamanos()
        return jsonify({
            'success': True,
            'tamanos': tamanos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/productos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_producto():
    try:
        # Print form data for debugging
        print("Form data:", request.form)
        print("Files:", request.files)
        
        id_producto = request.form.get('id')
        nombre = request.form.get('nombreProducto')
        descripcion = request.form.get('descripcionProducto')
        precio = float(request.form.get('precioProducto'))
        stock = int(request.form.get('stockProducto') or 0)
        stock_min = int(request.form.get('stockMinProducto') or 0)
        stock_max = int(request.form.get('stockMaxProducto') or 0)
        categoria_id = int(request.form.get('categoriaProducto'))
        tamano_id = int(request.form.get('tamano_id'))
        
        # Manejar la imagen
        ruta_imagen = None
        if 'imagenProducto' in request.files:
            archivo = request.files['imagenProducto']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = secure_filename(timestamp + '.' + archivo.filename.rsplit('.', 1)[1].lower())
                
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                archivo.save(os.path.join(upload_folder, filename))
                ruta_imagen = f'/static/images/productos/{filename}'
        
        if id_producto:  # Editar producto existente
            producto_actual = obtener_producto_por_id(id_producto)
            
            if not ruta_imagen and producto_actual and producto_actual.get('ruta_imagen'):
                ruta_imagen = producto_actual['ruta_imagen']
            
            # Actualizar el producto principal
            resultado, mensaje = actualizar_producto(
                id_producto, nombre, descripcion, precio, 
                stock, stock_min, stock_max, categoria_id, ruta_imagen
            )
            
            # Manejar la variante del tamaño
            if tamano_id and tamano_id != 4:  # 4 es "No Aplica"
                # Eliminar todas las variantes existentes primero
                eliminar_variantes_producto(id_producto)
                # Crear nueva variante con el tamaño seleccionado
                agregar_variante_producto(id_producto, tamano_id, precio)
            elif tamano_id == 4:  # Si seleccionó "No Aplica"
                eliminar_variantes_producto(id_producto)
        else:  # Crear nuevo producto
            resultado, nuevo_id = agregar_producto(
                nombre, descripcion, precio, stock, 
                stock_min, stock_max, categoria_id, ruta_imagen
            )
            
            if resultado and tamano_id and tamano_id != 4:
                agregar_variante_producto(nuevo_id, tamano_id, precio)
                
            mensaje = 'Producto creado exitosamente' if resultado else 'Error al crear producto'
        
        return jsonify({
            'success': resultado,
            'message': mensaje
        })
    except Exception as e:
        print(f"Error en guardar_producto: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/productos/eliminar', methods=['POST'])
@login_required
def eliminar_producto_route():
    try:
        data = request.json
        id_producto = data.get('id')
        
        # Primero eliminar las variantes asociadas
        eliminar_variantes_producto(id_producto)
        
        # Luego eliminar el producto
        resultado = eliminar_producto(id_producto)
        
        return jsonify({
            'success': resultado,
            'message': 'Producto eliminado exitosamente' if resultado else 'Error al eliminar producto'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/productos/variantes', methods=['POST'])
@login_required
def guardar_variante():
    try:
        data = request.json
        producto_id = data.get('producto_id')
        tamano_id = data.get('tamano_id')
        precio = data.get('precio')
        
        resultado = agregar_variante_producto(producto_id, tamano_id, precio)
        
        return jsonify({
            'success': resultado,
            'message': 'Variante agregada exitosamente' if resultado else 'Error al agregar variante'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/productos/variantes/<int:producto_id>', methods=['GET'])
@login_required
def obtener_variantes(producto_id):
    try:
        variantes = obtener_variantes_por_producto(producto_id)
        
        return jsonify({
            'success': True,
            'variantes': variantes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/productos/<int:id>', methods=['GET'])
@login_required
def get_producto(id):
    try:
        producto = obtener_producto_por_id(id)
        if producto:
            # Obtener también las variantes del producto
            variantes = obtener_variantes_por_producto(id)
            return jsonify({
                'success': True,
                'producto': producto,
                'variantes': variantes
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@productos_bp.route('/api/categorias/<int:id>', methods=['GET'])
@login_required
def get_categoria(id):
    try:
        categorias = obtener_categorias()
        categoria = next((cat for cat in categorias if cat['Id'] == id), None)
        
        if categoria:
            return jsonify({
                'success': True,
                'categoria': categoria
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Categoría no encontrada'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
