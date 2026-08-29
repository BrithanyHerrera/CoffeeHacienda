# Ventas: órdenes, pedidos y detalle
import logging
from decimal import Decimal, InvalidOperation

from bd import Conexion_BD

logger = logging.getLogger(__name__)


def _detalle_tiene_variante_id(cursor):
    """Permite desplegar el código antes o después de aplicar la migración."""
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tdetalleventas'
          AND COLUMN_NAME = 'variante_id'
    """)
    resultado = cursor.fetchone()
    return bool(resultado and resultado['total'])


def _entero_positivo(valor, campo):
    """Convierte enteros de JSON sin aceptar booleanos, decimales ni negativos."""
    if isinstance(valor, bool):
        raise ValueError(f'{campo} no es válido')

    if isinstance(valor, int):
        numero = valor
    elif isinstance(valor, str) and valor.strip().isdigit():
        numero = int(valor.strip())
    else:
        raise ValueError(f'{campo} debe ser un número entero')

    if numero <= 0:
        raise ValueError(f'{campo} debe ser mayor que cero')
    return numero


def _monto_no_negativo(valor, campo):
    """Convierte importes a Decimal y rechaza NaN, infinito y negativos."""
    if isinstance(valor, bool):
        raise ValueError(f'{campo} no es válido')

    try:
        monto = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f'{campo} no es válido')

    if not monto.is_finite() or monto < 0:
        raise ValueError(f'{campo} no es válido')
    return monto.quantize(Decimal('0.01'))


def obtener_ordenes_pendientes():
    """Obtiene órdenes con estado Pendiente (1) o En proceso (2)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
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
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener órdenes pendientes: {e}")
        return []
    finally:
        conn.close()

def actualizar_estado_orden(orden_id, nuevo_estado_id):
    """Cambia el estado respetando la transición aun con solicitudes simultáneas."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT estado_id FROM tventas WHERE Id = %s FOR UPDATE", (orden_id,))
            orden = cursor.fetchone()
            if not orden:
                conn.rollback()
                return False

            estado_actual = orden['estado_id']
            if estado_actual == nuevo_estado_id:
                conn.commit()
                return True

            origenes_permitidos = {
                2: (1,),  # Pendiente -> En proceso
                4: (2,),  # En proceso -> Completado
            }
            if estado_actual not in origenes_permitidos.get(nuevo_estado_id, ()):
                conn.rollback()
                return False

            cursor.execute(
                "UPDATE tventas SET estado_id = %s WHERE Id = %s AND estado_id = %s",
                (nuevo_estado_id, orden_id, estado_actual)
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al actualizar estado de orden: {e}")
        return False
    finally:
        conn.close()

def obtener_detalle_orden(orden_id):
    """Obtiene los productos de una orden con precios y tamaños."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            if _detalle_tiene_variante_id(cursor):
                cursor.execute("""
                    SELECT d.producto_id, d.variante_id,
                           COALESCE(d.producto_nombre_snapshot, p.nombre_producto) AS nombre_producto,
                           d.cantidad, d.precio,
                           (d.cantidad * d.precio) AS subtotal,
                           COALESCE(d.tamano_snapshot, t.tamano, 'No aplica') AS tamano
                    FROM tdetalleventas d
                    JOIN tproductos p ON d.producto_id = p.Id
                    LEFT JOIN tproductos_variantes pv ON d.variante_id = pv.Id
                    LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
                    WHERE d.venta_id = %s
                    ORDER BY d.Id
                """, (orden_id,))
            else:
                cursor.execute("""
                    SELECT d.producto_id, NULL AS variante_id, p.nombre_producto,
                           d.cantidad, d.precio,
                           (d.cantidad * d.precio) AS subtotal, NULL AS tamano
                    FROM tdetalleventas d
                    JOIN tproductos p ON d.producto_id = p.Id
                    WHERE d.venta_id = %s
                    ORDER BY d.Id
                """, (orden_id,))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener detalles de orden: {e}")
        return []
    finally:
        conn.close()


def obtener_estado_orden(orden_id):
    """Devuelve el estado_id actual de una orden."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT estado_id FROM tventas WHERE Id = %s", (orden_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def cancelar_orden(orden_id, usuario_id, motivo):
    """Cancela una orden, repone stock y registra auditoría exactamente una vez."""
    motivo = (motivo or '').strip() if isinstance(motivo, str) else ''
    if len(motivo) < 3 or len(motivo) > 255:
        return False

    try:
        usuario_id = _entero_positivo(usuario_id, 'Usuario')
    except ValueError:
        return False

    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT estado_id FROM tventas WHERE Id = %s FOR UPDATE", (orden_id,))
            orden = cursor.fetchone()
            if not orden:
                conn.rollback()
                return False

            estado_actual = orden['estado_id']
            if estado_actual == 3:
                # Una repetición no vuelve a sumar existencias.
                conn.commit()
                return True
            if estado_actual not in (1, 2):
                conn.rollback()
                return False

            cursor.execute("""
                SELECT dv.producto_id, SUM(dv.cantidad) AS cantidad
                FROM tdetalleventas dv
                JOIN tproductos p ON dv.producto_id = p.Id
                JOIN tcategorias c ON p.categoria_id = c.Id
                WHERE dv.venta_id = %s
                  AND c.requiere_inventario = 1
                GROUP BY dv.producto_id
                ORDER BY dv.producto_id
            """, (orden_id,))
            productos_a_reponer = cursor.fetchall()

            for producto in productos_a_reponer:
                cursor.execute(
                    "UPDATE tproductos SET stock = stock + %s WHERE Id = %s",
                    (producto['cantidad'], producto['producto_id'])
                )
                if cursor.rowcount != 1:
                    raise RuntimeError(
                        f"No se pudo reponer el producto {producto['producto_id']}"
                    )

                cursor.execute("""
                    INSERT INTO tmovimientosinventario
                        (producto_id, venta_id, usuario_id, cantidad,
                         tipo_movimiento_id, motivo)
                    VALUES (%s, %s, %s, %s, 1, %s)
                """, (
                    producto['producto_id'], orden_id, usuario_id,
                    producto['cantidad'], f'Cancelación de venta: {motivo}'
                ))

            cursor.execute(
                """
                UPDATE tventas
                SET estado_id = 3,
                    cancelado_por_id = %s,
                    cancelado_en = NOW(),
                    motivo_cancelacion = %s
                WHERE Id = %s AND estado_id = %s
                """,
                (usuario_id, motivo, orden_id, estado_actual)
            )
            if cursor.rowcount != 1:
                raise RuntimeError('La orden cambió mientras se intentaba cancelar')
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al cancelar orden: {e}")
        return False
    finally:
        conn.close()


def eliminar_orden(orden_id, usuario_id, motivo):
    """Alias conservado: ya no elimina datos, realiza una cancelación segura."""
    return cancelar_orden(orden_id, usuario_id, motivo)


def obtener_vendedores_activos():
    """Lista de vendedores activos (para filtros del historial)."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT usuario FROM tusuarios WHERE activo = 1 ORDER BY usuario")
            return cursor.fetchall()
    finally:
        conn.close()


def obtener_venta_completa(venta_id):
    """Devuelve (venta, detalles) con toda la info para el modal de detalle."""
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
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
                return None, None

            if _detalle_tiene_variante_id(cursor):
                cursor.execute("""
                    SELECT COALESCE(dv.producto_nombre_snapshot, p.nombre_producto) AS nombre_producto,
                           dv.variante_id, dv.precio,
                           COALESCE(dv.tamano_snapshot, t.tamano, 'No aplica') AS tamano,
                           dv.cantidad, (dv.precio * dv.cantidad) AS subtotal
                    FROM tdetalleventas dv
                    JOIN tproductos p ON dv.producto_id = p.Id
                    LEFT JOIN tproductos_variantes pv ON dv.variante_id = pv.Id
                    LEFT JOIN ttamanos t ON pv.tamano_id = t.Id
                    WHERE dv.venta_id = %s
                    ORDER BY dv.Id
                """, (venta_id,))
            else:
                cursor.execute("""
                    SELECT p.nombre_producto, NULL AS variante_id, dv.precio,
                           NULL AS tamano, dv.cantidad,
                           (dv.precio * dv.cantidad) AS subtotal
                    FROM tdetalleventas dv
                    JOIN tproductos p ON dv.producto_id = p.Id
                    WHERE dv.venta_id = %s
                    ORDER BY dv.Id
                """, (venta_id,))
            detalles = cursor.fetchall()

            return venta, detalles
    except Exception as e:
        logger.error(f"Error al obtener venta completa: {e}")
        return None, None
    finally:
        conn.close()


def procesar_venta_completa(nombre_cliente, numero_mesa, productos, total,
                            metodo_pago_id, usuario_actual, dinero_recibido=0, cambio=0):
    """Registra una venta usando exclusivamente precios y cálculos del servidor.

    ``total`` y ``cambio`` se conservan en la firma para compatibilidad con llamadas
    anteriores, pero se ignoran deliberadamente porque provienen del cliente.
    """
    conn = Conexion_BD()
    try:
        with conn.cursor() as cursor:
            if not isinstance(productos, list) or not productos:
                return False, 'No se proporcionaron productos válidos', None
            if len(productos) > 100:
                return False, 'La venta excede el máximo de 100 partidas', None

            try:
                metodo_pago_id = _entero_positivo(metodo_pago_id, 'Método de pago')
            except ValueError as error:
                return False, str(error), None

            cursor.execute(
                "SELECT Id, codigo, tipo_de_pago FROM tmetodospago WHERE Id = %s",
                (metodo_pago_id,)
            )
            metodo_pago = cursor.fetchone()
            if not metodo_pago:
                return False, 'Método de pago no válido', None

            solicitudes = {}
            try:
                for indice, producto in enumerate(productos, start=1):
                    if not isinstance(producto, dict):
                        raise ValueError(f'Producto {indice} no es válido')

                    producto_id = _entero_positivo(producto.get('id'), f'ID del producto {indice}')
                    cantidad = _entero_positivo(producto.get('cantidad'), f'Cantidad del producto {indice}')
                    variante_valor = producto.get('variante_id')
                    variante_id = None
                    if variante_valor not in (None, ''):
                        variante_id = _entero_positivo(
                            variante_valor, f'Variante del producto {indice}'
                        )

                    clave = (producto_id, variante_id)
                    solicitudes[clave] = solicitudes.get(clave, 0) + cantidad
            except ValueError as error:
                return False, str(error), None

            producto_ids = sorted({clave[0] for clave in solicitudes})
            placeholders = ', '.join(['%s'] * len(producto_ids))

            cursor.execute(f"""
                SELECT p.Id AS id, p.nombre_producto, p.precio, p.stock,
                       c.requiere_inventario
                FROM tproductos p
                JOIN tcategorias c ON p.categoria_id = c.Id
                WHERE p.Id IN ({placeholders}) AND p.activo = 1
                ORDER BY p.Id
                FOR UPDATE
            """, producto_ids)
            productos_db = {fila['id']: fila for fila in cursor.fetchall()}

            ids_faltantes = [producto_id for producto_id in producto_ids if producto_id not in productos_db]
            if ids_faltantes:
                return False, f'Producto no disponible: {ids_faltantes[0]}', None

            cursor.execute(f"""
                SELECT pv.Id AS id, pv.producto_id, pv.precio, t.tamano
                FROM tproductos_variantes pv
                JOIN ttamanos t ON pv.tamano_id = t.Id
                WHERE pv.producto_id IN ({placeholders})
                ORDER BY pv.producto_id, pv.Id
                FOR UPDATE
            """, producto_ids)
            variantes_por_producto = {producto_id: {} for producto_id in producto_ids}
            for variante in cursor.fetchall():
                variantes_por_producto[variante['producto_id']][variante['id']] = variante

            productos_validos = []
            cantidad_inventario = {}
            total_calculado = Decimal('0.00')

            for (producto_id, variante_id), cantidad in solicitudes.items():
                producto_db = productos_db[producto_id]
                variantes = variantes_por_producto[producto_id]

                if variantes:
                    if variante_id is None:
                        return False, (
                            f'Debe seleccionar una variante para {producto_db["nombre_producto"]}'
                        ), None
                    variante = variantes.get(variante_id)
                    if not variante:
                        return False, (
                            f'La variante seleccionada no pertenece a {producto_db["nombre_producto"]}'
                        ), None
                    precio = _monto_no_negativo(variante['precio'], 'Precio oficial')
                    tamano = variante['tamano']
                else:
                    if variante_id is not None:
                        return False, (
                            f'{producto_db["nombre_producto"]} no tiene esa variante'
                        ), None
                    precio = _monto_no_negativo(producto_db['precio'], 'Precio oficial')
                    tamano = None

                total_calculado += precio * cantidad
                productos_validos.append({
                    'id': producto_id,
                    'variante_id': variante_id,
                    'nombre': producto_db['nombre_producto'],
                    'tamano': tamano,
                    'cantidad': cantidad,
                    'precio': precio,
                })

                if producto_db['requiere_inventario'] == 1:
                    cantidad_inventario[producto_id] = (
                        cantidad_inventario.get(producto_id, 0) + cantidad
                    )

            total_calculado = total_calculado.quantize(Decimal('0.01'))
            productos_sin_stock = []
            for producto_id, cantidad in cantidad_inventario.items():
                producto_db = productos_db[producto_id]
                if producto_db['stock'] < cantidad:
                    productos_sin_stock.append({
                        'id': producto_id,
                        'nombre': producto_db['nombre_producto'],
                        'stock_actual': producto_db['stock'],
                        'cantidad_solicitada': cantidad
                    })

            if productos_sin_stock:
                mensaje = "No hay suficiente stock para los siguientes productos:\n"
                for p in productos_sin_stock:
                    mensaje += f"- {p['nombre']}: Stock actual: {p['stock_actual']}, Solicitado: {p['cantidad_solicitada']}\n"
                return False, mensaje, {'productos_sin_stock': productos_sin_stock}

            if metodo_pago['codigo'] == 'EFECTIVO':
                try:
                    dinero_recibido_calculado = _monto_no_negativo(
                        dinero_recibido, 'Dinero recibido'
                    )
                except ValueError as error:
                    return False, str(error), None
                if dinero_recibido_calculado < total_calculado:
                    return False, 'El dinero recibido es menor al total de la venta', None
                cambio_calculado = dinero_recibido_calculado - total_calculado
            else:
                dinero_recibido_calculado = Decimal('0.00')
                cambio_calculado = Decimal('0.00')

            nombre_cliente = (nombre_cliente or '').strip() if isinstance(nombre_cliente, str) else ''
            if not nombre_cliente:
                nombre_cliente = 'Cliente General'
            nombre_cliente = nombre_cliente[:255]

            numero_mesa = (numero_mesa or '').strip() if isinstance(numero_mesa, str) else ''
            numero_mesa = numero_mesa[:50]

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
            if not usuario_db:
                return False, 'El vendedor de la sesión ya no está disponible', None
            vendedor_id = usuario_db['Id']

            # Estado inicial
            cursor.execute("SELECT Id FROM testadosventa WHERE Id = 1")
            estado_result = cursor.fetchone()
            if not estado_result:
                return False, 'No existe el estado inicial Pendiente', None
            estado_id = estado_result['Id']

            # Registrar venta
            cursor.execute("""
                INSERT INTO tventas (cliente_id, vendedor_id, total, metodo_pago_id, 
                                     numero_mesa, estado_id, dinero_recibido, cambio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente_id, vendedor_id, total_calculado, metodo_pago_id,
                numero_mesa, estado_id, dinero_recibido_calculado, cambio_calculado
            ))

            venta_id = cursor.lastrowid

            # Detalles y descuento de stock
            detalle_con_variante = _detalle_tiene_variante_id(cursor)
            for prod in productos_validos:
                if detalle_con_variante:
                    cursor.execute("""
                        INSERT INTO tdetalleventas
                            (venta_id, producto_id, variante_id,
                             producto_nombre_snapshot, tamano_snapshot,
                             cantidad, precio)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        venta_id, prod['id'], prod['variante_id'],
                        prod['nombre'], prod['tamano'] or 'No aplica',
                        prod['cantidad'], prod['precio']
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO tdetalleventas (venta_id, producto_id, cantidad, precio)
                        VALUES (%s, %s, %s, %s)
                    """, (venta_id, prod['id'], prod['cantidad'], prod['precio']))

            for producto_id, cantidad in cantidad_inventario.items():
                cursor.execute("""
                    UPDATE tproductos
                    SET stock = stock - %s
                    WHERE Id = %s AND stock >= %s
                """, (cantidad, producto_id, cantidad))
                if cursor.rowcount != 1:
                    raise RuntimeError(
                        f'No se pudo reservar el inventario del producto {producto_id}'
                    )

                cursor.execute("""
                    INSERT INTO tmovimientosinventario
                        (producto_id, venta_id, usuario_id, cantidad,
                         tipo_movimiento_id, motivo)
                    VALUES (%s, %s, %s, %s, 2, %s)
                """, (
                    producto_id, venta_id, vendedor_id, cantidad,
                    'Salida por venta'
                ))

        conn.commit()
        return True, 'Venta registrada exitosamente', {
            'venta_id': venta_id,
            'total': f'{total_calculado:.2f}',
            'dinero_recibido': f'{dinero_recibido_calculado:.2f}',
            'cambio': f'{cambio_calculado:.2f}',
            'productos': [{
                'id': prod['id'],
                'variante_id': prod['variante_id'],
                'nombre': prod['nombre'],
                'tamano': prod['tamano'] or 'No aplica',
                'cantidad': prod['cantidad'],
                'precio': f'{prod["precio"]:.2f}',
            } for prod in productos_validos]
        }

    except Exception as e:
        conn.rollback()
        logger.error(f"Error al procesar venta: {e}")
        raise
    finally:
        conn.close()
