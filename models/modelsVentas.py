# Modelo de ventas — órdenes, procesamiento de pedidos y consultas de detalle
import logging
from bd import Conexion_BD

logger = logging.getLogger(__name__)


def obtener_ordenes_pendientes():
    """Obtiene órdenes con estado Pendiente (1) o En proceso (2)."""
    try:
        conn = Conexion_BD()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.fecha_hora, v.total, u.usuario AS vendedor, c.nombre AS cliente,
                   v.numero_mesa, e.estado, m.tipo_de_pago AS metodo_pago,
                   COALESCE(v.dinero_recibido, 0) AS dinero_recibido,
                   COALESCE(v.cambio, 0) AS cambio
            FROM tventas v
            JOIN tusuarios u ON v.vendedor_id = u.id
            JOIN tclientes c ON v.cliente_id = c.id
            JOIN testadosventa e ON v.estado_id = e.id
            JOIN tmetodospago m ON v.metodo_pago_id = m.id
            WHERE v.estado_id IN (1, 2)
            ORDER BY v.fecha_hora DESC
        """)
        ordenes = cursor.fetchall()
        cursor.close()
        conn.close()
        return ordenes
    except Exception as e:
        logger.error(f"Error al obtener órdenes pendientes: {e}")
        return []

def actualizar_estado_orden(orden_id, nuevo_estado_id):
    """Cambia el estado de una orden."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tventas SET estado_id = %s WHERE Id = %s", (nuevo_estado_id, orden_id))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar estado de orden: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        conn.close()

def obtener_detalle_orden(orden_id):
    """Obtiene los productos de una orden con precios y tamaños."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.producto_id, p.nombre_producto, d.cantidad, d.precio, 
                   (d.cantidad * d.precio) as subtotal, t.tamano
            FROM tdetalleventas d
            JOIN tproductos p ON d.producto_id = p.Id
            LEFT JOIN tproductos_variantes pv ON p.id = pv.producto_id
            LEFT JOIN ttamanos t ON pv.tamano_id = t.id
            WHERE d.venta_id = %s
        """, (orden_id,))
        detalles = cursor.fetchall()
        cursor.close()
        return detalles
    except Exception as e:
        logger.error(f"Error al obtener detalles de orden: {e}")
        return []
    finally:
        conn.close()


def obtener_estado_orden(orden_id):
    """Devuelve el estado_id actual de una orden."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT estado_id FROM tventas WHERE Id = %s", (orden_id,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado
    finally:
        conn.close()


def eliminar_orden(orden_id):
    """Elimina una orden (CASCADE borra los detalles automáticamente)."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tventas WHERE Id = %s", (orden_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al eliminar orden: {e}")
        return False
    finally:
        conn.close()


def obtener_vendedores_activos():
    """Lista de vendedores activos (para filtros del historial)."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT usuario FROM tusuarios WHERE activo = 1 ORDER BY usuario")
        vendedores = cursor.fetchall()
        cursor.close()
        return vendedores
    finally:
        conn.close()


def obtener_venta_completa(venta_id):
    """Devuelve (venta, detalles) con toda la info para el modal de detalle."""
    conn = Conexion_BD()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT v.Id, v.total, v.fecha_hora, v.numero_mesa,
                   c.nombre AS cliente, u.usuario AS vendedor,
                   mp.tipo_de_pago AS metodo_pago,
                   COALESCE(v.dinero_recibido, 0) AS dinero_recibido,
                   COALESCE(v.cambio, 0) AS cambio
            FROM tventas v
            LEFT JOIN tclientes c ON v.cliente_id = c.Id
            LEFT JOIN tusuarios u ON v.vendedor_id = u.Id
            LEFT JOIN tmetodospago mp ON v.metodo_pago_id = mp.Id
            WHERE v.Id = %s
        """, (venta_id,))
        venta = cursor.fetchone()

        if not venta:
            cursor.close()
            return None, None

        cursor.execute("""
            SELECT p.nombre_producto, pv.precio, t.tamano,
                   dv.cantidad, (dv.precio * dv.cantidad) AS subtotal
            FROM tdetalleventas dv
            JOIN tproductos p ON dv.producto_id = p.Id
            LEFT JOIN tproductos_variantes pv ON dv.producto_id = pv.producto_id
            LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
            WHERE dv.venta_id = %s
        """, (venta_id,))
        detalles = cursor.fetchall()

        cursor.close()
        return venta, detalles
    except Exception as e:
        logger.error(f"Error al obtener venta completa: {e}")
        return None, None
    finally:
        conn.close()


def procesar_venta_completa(nombre_cliente, numero_mesa, productos, total,
                            metodo_pago_id, usuario_actual, dinero_recibido=0, cambio=0):
    """Procesa un pedido completo: valida stock, crea cliente, registra venta y detalles."""
    conn = Conexion_BD()
    cursor = conn.cursor()

    try:
        productos_validos = []
        productos_sin_stock = []

        for producto in productos:
            producto_id = int(producto['id'])
            cantidad_solicitada = int(producto['cantidad'])

            cursor.execute("""
                SELECT p.Id, p.nombre_producto, p.stock, c.requiere_inventario, c.categoria
                FROM tproductos p
                JOIN tcategorias c ON p.categoria_id = c.id
                WHERE p.Id = %s
            """, (producto_id,))
            resultado = cursor.fetchone()

            if not resultado:
                cursor.close()
                conn.close()
                return False, f'Producto con ID {producto_id} no encontrado', None

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

        if productos_sin_stock:
            cursor.close()
            conn.close()
            mensaje = "No hay suficiente stock para los siguientes productos:\n"
            for p in productos_sin_stock:
                mensaje += f"- {p['nombre']}: Stock actual: {p['stock_actual']}, Solicitado: {p['cantidad_solicitada']}\n"
            return False, mensaje, {'productos_sin_stock': productos_sin_stock}

        if not productos_validos:
            cursor.close()
            conn.close()
            return False, 'No hay productos válidos para registrar la venta', None

        # Obtener o crear cliente
        cursor.execute("SELECT Id FROM tclientes WHERE nombre = %s", (nombre_cliente,))
        cliente = cursor.fetchone()
        if cliente:
            cliente_id = cliente['Id']
        else:
            cursor.execute("INSERT INTO tclientes (nombre) VALUES (%s)", (nombre_cliente,))
            cliente_id = cursor.lastrowid

        # Vendedor
        cursor.execute("SELECT Id FROM tusuarios WHERE usuario = %s", (usuario_actual,))
        usuario_db = cursor.fetchone()
        vendedor_id = usuario_db['Id'] if usuario_db else 1

        # Estado inicial
        cursor.execute("SELECT Id FROM testadosventa LIMIT 1")
        estado_result = cursor.fetchone()
        estado_id = estado_result['Id'] if estado_result else 4

        # Registrar venta
        cursor.execute("""
            INSERT INTO tventas (cliente_id, vendedor_id, total, metodo_pago_id, 
                                 numero_mesa, estado_id, dinero_recibido, cambio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (cliente_id, vendedor_id, total, metodo_pago_id, numero_mesa, estado_id, dinero_recibido, cambio))

        venta_id = cursor.lastrowid

        # Detalles y descuento de stock
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

        return True, 'Venta registrada exitosamente', {'venta_id': venta_id}

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise e