from flask import Blueprint, render_template, request, jsonify, session
from bd import Conexion_BD
from utils import login_required, admin_required
from models.modelsProductosMenu import obtener_productos_menu
from models.modelsVentas import (crear_venta, obtener_cliente_por_nombre, 
                                obtener_ordenes_pendientes, actualizar_estado_orden,
                                obtener_detalle_orden)
from models.modelsHistorial import obtener_historial_ventas, obtener_detalle_venta

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/menu')
@login_required
def menu():
    nombre_usuario = session['usuario']
    productos = obtener_productos_menu()
    return render_template('menu.html', nombre_usuario=nombre_usuario, productos=productos)

@ventas_bp.route('/ordenes')
@login_required
def ordenes():
    # Obtener órdenes pendientes
    ordenes_pendientes = obtener_ordenes_pendientes()
    return render_template('ordenes.html', ordenes=ordenes_pendientes)

@ventas_bp.route('/api/ordenes', methods=['GET'])
@login_required
def api_obtener_ordenes():
    try:
        ordenes = obtener_ordenes_pendientes()
        return jsonify({
            'success': True,
            'ordenes': ordenes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@ventas_bp.route('/api/ordenes/<int:id>/detalles', methods=['GET'])
@login_required
def api_detalle_orden(id):
    try:
        detalles = obtener_detalle_orden(id)
        if detalles:
            return jsonify({
                'success': True,
                'detalles': detalles
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Orden no encontrada'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@ventas_bp.route('/api/ordenes/<int:id>/estado', methods=['POST'])
@login_required
def api_actualizar_estado_orden(id):
    try:
        data = request.json
        nuevo_estado = data.get('estado')
        
        # Mapear nombres de estado a IDs
        estados = {
            'Pendiente': 1,
            'En proceso': 2,
            'Cancelado': 3,
            'Completado': 4,
            'Reembolsada': 5
        }
        
        if nuevo_estado not in estados:
            return jsonify({
                'success': False,
                'message': 'Estado no válido'
            })
        
        # Obtener el estado actual de la orden
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("SELECT estado_id FROM tventas WHERE Id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not resultado:
            return jsonify({
                'success': False,
                'message': 'Orden no encontrada'
            })
        
        estado_actual_id = resultado['estado_id']
        
        # Definir transiciones válidas
        transiciones_validas = {
            1: [2, 3],           # Pendiente -> En proceso, Cancelado
            2: [3, 4],           # En proceso -> Cancelado, Completado
            3: [],               # Cancelado -> (ninguno)
            4: [],               # Completado -> (ninguno)
            5: []                # Reembolsada -> (ninguno)
        }
        
        # Verificar si la transición es válida
        if estados[nuevo_estado] not in transiciones_validas[estado_actual_id] and estados[nuevo_estado] != estado_actual_id:
            # Obtener nombre del estado actual
            estado_actual_nombre = next((nombre for nombre, id in estados.items() if id == estado_actual_id), "Desconocido")
            
            # Obtener nombres de estados válidos
            estados_validos = [next((nombre for nombre, id in estados.items() if id == estado_id), "Desconocido") 
                            for estado_id in transiciones_validas[estado_actual_id]]
            
            mensaje_estados = ", ".join(estados_validos) if estados_validos else "ninguno"
            
            return jsonify({
                'success': False,
                'message': f'Transición no válida. Desde "{estado_actual_nombre}" solo puede cambiar a: {mensaje_estados}'
            })
        
        # Si el nuevo estado es "Cancelado", eliminar la orden y sus detalles
        if nuevo_estado == 'Cancelado':
            conn = Conexion_BD()
            cursor = conn.cursor()
            
            # Primero eliminar los detalles de la venta (debido a la restricción de clave foránea)
            cursor.execute("DELETE FROM tdetalleventas WHERE venta_id = %s", (id,))
            
            # Luego eliminar la venta
            cursor.execute("DELETE FROM tventas WHERE Id = %s", (id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Orden cancelada y eliminada del sistema'
            })
        else:
            # Si no es cancelación, actualizar el estado normalmente
            resultado = actualizar_estado_orden(id, estados[nuevo_estado])
            
            if resultado:
                return jsonify({
                    'success': True,
                    'message': f'Estado actualizado a {nuevo_estado}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error al actualizar estado'
                })
    except Exception as e:
        print(f"Error al actualizar estado de orden: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@ventas_bp.route('/historial')
@login_required
def historial():
    # Obtener la lista de vendedores para el filtro
    conn = Conexion_BD()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT usuario FROM tusuarios WHERE activo = 1 ORDER BY usuario")
    vendedores = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('historial.html', vendedores=vendedores)

@ventas_bp.route('/historial-ventas')
@login_required
@admin_required
def historial_ventas():
    return render_template('historial.html')

@ventas_bp.route('/api/historial-ventas', methods=['GET'])
@login_required
def api_historial_ventas():
    filtro_cliente = request.args.get('cliente', '')
    filtro_vendedor = request.args.get('vendedor', '')
    fecha_inicio = request.args.get('fechaInicio', '')
    fecha_fin = request.args.get('fechaFin', '')

    try:
        ventas = obtener_historial_ventas(filtro_cliente, fecha_inicio, fecha_fin)
        return jsonify({'success': True, 'ventas': ventas})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@ventas_bp.route('/api/historial-ventas/<int:id>', methods=['GET'])
@login_required
def api_detalle_venta(id):
    try:
        # Obtener detalles básicos de la venta
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        # Consulta para obtener información principal de la venta
        cursor.execute("""
            SELECT 
                v.Id, 
                v.total, 
                v.fecha_hora, 
                v.numero_mesa,
                c.nombre AS cliente,
                u.usuario AS vendedor,
                mp.tipo_de_pago AS metodo_pago,
                v.total AS dinero_recibido,
                v.total AS cambio  -- Aquí deberías ajustar según tu lógica de negocio
            FROM tventas v
            LEFT JOIN tclientes c ON v.cliente_id = c.Id
            LEFT JOIN tusuarios u ON v.vendedor_id = u.Id
            LEFT JOIN tmetodospago mp ON v.metodo_pago_id = mp.Id
            WHERE v.Id = %s
        """, (id,))
        venta = cursor.fetchone()
        
        if not venta:
            return jsonify({'success': False, 'message': 'Venta no encontrada'})
        
        # Obtener detalles de los productos vendidos
        cursor.execute("""
            SELECT 
                p.nombre_producto,
                pv.precio,
                t.tamano,
                dv.cantidad,
                (dv.precio * dv.cantidad) AS subtotal
            FROM tdetalleventas dv
            JOIN tproductos p ON dv.producto_id = p.Id
            LEFT JOIN tproductos_variantes pv ON dv.producto_id = pv.producto_id
            LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
            WHERE dv.venta_id = %s
        """, (id,))
        detalles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'venta': venta,
            'detalles': detalles
        })
    except Exception as e:
        print(f"Error al obtener detalles de venta: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Ruta para procesar ventas desde el menú
@ventas_bp.route('/api/ventas/crear', methods=['POST'])
@login_required
def procesar_venta():
    try:
        data = request.json
        print("Datos recibidos:", data)
        
        nombre_cliente = data.get('cliente', 'Cliente General')
        numero_mesa = data.get('mesa', '')
        productos = data.get('productos', [])
        total = data.get('total', 0)
        metodo_pago_id = data.get('metodo_pago', 1)
        
        if not productos:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron productos'
            })
        
        # UNA SOLA conexión para toda la operación
        conn = Conexion_BD()
        cursor = conn.cursor()
        
        try:
            productos_validos = []
            productos_invalidos = []
            productos_sin_stock = []
            
            for producto in productos:
                producto_id = int(producto['id'])
                cantidad_solicitada = int(producto['cantidad'])
                
                # Verificar producto y su categoría
                cursor.execute("""
                    SELECT p.Id, p.nombre_producto, p.stock, c.requiere_inventario, c.categoria
                    FROM tproductos p
                    JOIN tcategorias c ON p.categoria_id = c.id
                    WHERE p.Id = %s
                """, (producto_id,))
                resultado = cursor.fetchone()
                
                if resultado:
                    requiere_stock = resultado['requiere_inventario'] == 1 or resultado['categoria'] in ['Postre', 'Snack']
                    
                    if requiere_stock and resultado['stock'] < cantidad_solicitada:
                        productos_sin_stock.append({
                            'id': producto_id,
                            'nombre': resultado['nombre_producto'],
                            'stock_actual': resultado['stock'],
                            'cantidad_solicitada': cantidad_solicitada
                        })
                    else:
                        productos_validos.append({
                            'id': producto_id,
                            'cantidad': cantidad_solicitada,
                            'precio': float(producto['precio'])
                        })
                else:
                    productos_invalidos.append(producto_id)
                    print(f"Producto con ID {producto_id} no encontrado en la base de datos")
            
            if productos_sin_stock:
                cursor.close()
                conn.close()
                mensaje_error = "No hay suficiente stock para los siguientes productos:\n"
                for p in productos_sin_stock:
                    mensaje_error += f"- {p['nombre']}: Stock actual: {p['stock_actual']}, Solicitado: {p['cantidad_solicitada']}\n"
                
                return jsonify({
                    'success': False,
                    'message': mensaje_error,
                    'productos_sin_stock': productos_sin_stock
                })
            
            if productos_invalidos:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'message': f'Los siguientes productos no existen en la base de datos: {productos_invalidos}'
                })
            
            # Obtener o crear cliente (reutilizando la misma conexión)
            cursor.execute("SELECT Id FROM tclientes WHERE nombre = %s", (nombre_cliente,))
            cliente = cursor.fetchone()
            
            if cliente:
                cliente_id = cliente['Id']
            else:
                cursor.execute("INSERT INTO tclientes (nombre) VALUES (%s)", (nombre_cliente,))
                cliente_id = cursor.lastrowid
            
            # Obtener vendedor_id (reutilizando la misma conexión)
            usuario_actual = session.get('usuario', '')
            cursor.execute("SELECT Id FROM tusuarios WHERE usuario = %s", (usuario_actual,))
            usuario_db = cursor.fetchone()
            vendedor_id = usuario_db['Id'] if usuario_db else 1
            
            # Obtener estado (reutilizando la misma conexión)
            cursor.execute("SELECT Id FROM testadosventa LIMIT 1")
            estado_result = cursor.fetchone()
            estado_id = estado_result['Id'] if estado_result else 4
            
            if productos_validos:
                # Insertar la venta
                cursor.execute("""
                    INSERT INTO tventas (cliente_id, vendedor_id, total, metodo_pago_id, numero_mesa, estado_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (cliente_id, vendedor_id, total, metodo_pago_id, numero_mesa, estado_id))
                
                venta_id = cursor.lastrowid
                
                # Insertar detalles y actualizar stock
                for prod in productos_validos:
                    cursor.execute("""
                        INSERT INTO tdetalleventas (venta_id, producto_id, cantidad, precio)
                        VALUES (%s, %s, %s, %s)
                    """, (venta_id, prod['id'], prod['cantidad'], prod['precio']))
                    
                    cursor.execute("""
                        UPDATE tproductos p
                        JOIN tcategorias c ON p.categoria_id = c.Id
                        SET p.stock = p.stock - %s
                        WHERE p.Id = %s AND c.requiere_inventario = 1
                    """, (prod['cantidad'], prod['id']))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Venta registrada exitosamente',
                    'venta_id': venta_id
                })
            else:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'No hay productos válidos para registrar la venta'
                })
        except Exception as inner_e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise inner_e
            
    except Exception as e:
        print(f"Error al procesar venta: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al registrar la venta: {str(e)}'
        })
