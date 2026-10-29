from decimal import Decimal

import pytest

from models import modelsVentas
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_auxiliares_numericos_venta_cubren_cadenas_y_montos_invalidos():
    assert modelsVentas._entero_positivo(' 2 ', 'Campo') == 2
    for value in (True, -1, 'NaN', 'Infinity'):
        with pytest.raises(ValueError):
            modelsVentas._monto_no_negativo(value, 'Monto')


def test_ordenes_pendientes_exito_y_error(monkeypatch):
    rows = [{'id': 1}]
    successful = connection_with_results(rows)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: successful)
    assert modelsVentas.obtener_ordenes_pendientes() == rows

    failed = _failing_connection()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: failed)
    assert modelsVentas.obtener_ordenes_pendientes() == []


def test_actualizar_estado_orden_ramas(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: missing)
    assert modelsVentas.actualizar_estado_orden(1, 2) is False

    same = connection_with_results({'estado_id': 2})
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: same)
    assert modelsVentas.actualizar_estado_orden(1, 2) is True

    invalid = connection_with_results({'estado_id': 1})
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: invalid)
    assert modelsVentas.actualizar_estado_orden(1, 4) is False

    no_update = connection_with_results({'estado_id': 1}, None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: no_update)
    assert modelsVentas.actualizar_estado_orden(1, 2) is False

    def handler(sql, params, cursor):
        if sql.startswith('SELECT estado_id'):
            return {'estado_id': 1}
        cursor.rowcount = 1

    successful = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: successful)
    assert modelsVentas.actualizar_estado_orden(1, 2) is True

    failed = _failing_connection()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: failed)
    assert modelsVentas.actualizar_estado_orden(1, 2) is False


def test_detalles_orden_esquema_nuevo_antiguo_y_error(monkeypatch):
    new_rows = [{'nombre_producto': 'Snapshot'}]
    migrated = connection_with_results({'total': 1}, new_rows)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: migrated)
    assert modelsVentas.obtener_detalle_orden(1) == new_rows
    assert 'producto_nombre_snapshot' in migrated.cursor_instance.calls[1][0]

    old_rows = [{'nombre_producto': 'Actual'}]
    legacy = connection_with_results(None, old_rows)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: legacy)
    assert modelsVentas.obtener_detalle_orden(1) == old_rows
    assert 'NULL AS variante_id' in legacy.cursor_instance.calls[1][0]

    failed = _failing_connection()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: failed)
    assert modelsVentas.obtener_detalle_orden(1) == []


def test_obtener_estado_orden_y_vendedores(monkeypatch):
    state = {'estado_id': 1}
    state_connection = connection_with_results(state)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: state_connection)
    assert modelsVentas.obtener_estado_orden(1) == state

    sellers = [{'usuario': 'ana'}]
    seller_connection = connection_with_results(sellers)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: seller_connection)
    assert modelsVentas.obtener_vendedores_activos() == sellers


@pytest.mark.parametrize('reason', ['', 'x', None, 'x' * 256])
def test_cancelar_orden_rechaza_motivo_invalido(reason):
    assert modelsVentas.cancelar_orden(1, 1, reason) is False


@pytest.mark.parametrize('user_id', [None, 0, True, 'abc'])
def test_cancelar_orden_rechaza_usuario_invalido(user_id):
    assert modelsVentas.cancelar_orden(1, user_id, 'Motivo válido') is False


def test_cancelar_orden_faltante_ya_cancelada_y_estado_invalido(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: missing)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False

    cancelled = connection_with_results({'estado_id': 3})
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: cancelled)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is True

    completed = connection_with_results({'estado_id': 4})
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: completed)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False


def test_cancelar_orden_hace_rollback_cuando_falla_actualizacion_stock_o_venta(monkeypatch):
    stock_failure = connection_with_results(
        {'estado_id': 1},
        [{'producto_id': 10, 'cantidad': 1}],
        None,
    )
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: stock_failure)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False
    assert stock_failure.rollbacks == 1

    sale_failure = connection_with_results({'estado_id': 1}, [], None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: sale_failure)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False

    failed = _failing_connection()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: failed)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False


def test_alias_eliminar_orden(monkeypatch):
    monkeypatch.setattr(modelsVentas, 'cancelar_orden', lambda *args: 'resultado')
    assert modelsVentas.eliminar_orden(1, 2, 'Motivo') == 'resultado'


def test_obtener_venta_completa_faltante_nueva_antigua_y_error(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: missing)
    assert modelsVentas.obtener_venta_completa(1) == (None, None)

    sale = {'Id': 1}
    details = [{'nombre_producto': 'Snapshot'}]
    migrated = connection_with_results(sale, {'total': 1}, details)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: migrated)
    assert modelsVentas.obtener_venta_completa(1) == (sale, details)

    legacy = connection_with_results(sale, None, details)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: legacy)
    assert modelsVentas.obtener_venta_completa(1) == (sale, details)

    failed = _failing_connection()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: failed)
    assert modelsVentas.obtener_venta_completa(1) == (None, None)


def _sale_connection(product_rows=None, variant_rows=None, method=None):
    method = method if method is not None else {
        'Id': 1,
        'codigo': 'EFECTIVO',
        'tipo_de_pago': 'Efectivo',
    }
    queue = [method]
    if product_rows is not Ellipsis:
        queue.append(product_rows if product_rows is not None else [])
    if variant_rows is not Ellipsis:
        queue.append(variant_rows if variant_rows is not None else [])
    return connection_with_results(*queue)


@pytest.mark.parametrize('products', [None, {}, [], 'invalid'])
def test_venta_rechaza_coleccion_productos_invalida(monkeypatch, products):
    connection = connection_with_results()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)
    result = modelsVentas.procesar_venta_completa(
        'Cliente', '1', products, 1, 1, 'seller'
    )
    assert result[0] is False


def test_venta_rechaza_demasiados_articulos_metodo_invalido_y_desconocido(monkeypatch):
    empty = connection_with_results()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: empty)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1}] * 101, 1, 1, 'seller'
    )[0] is False

    invalid = connection_with_results()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: invalid)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, True, 'seller'
    )[0] is False

    unknown = connection_with_results(None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: unknown)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, 1, 'seller'
    ) == (False, 'Método de pago no válido', None)


def test_venta_rechaza_elementos_no_diccionario_producto_faltante_y_desajuste_variantes(monkeypatch):
    method = {'Id': 1, 'codigo': 'TARJETA', 'tipo_de_pago': 'Tarjeta'}

    non_dict = connection_with_results(method)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: non_dict)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', ['bad'], 1, 1, 'seller'
    )[0] is False

    missing = _sale_connection([])
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: missing)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 9, 'cantidad': 1}], 1, 1, 'seller'
    ) == (False, 'Producto no disponible: 9', None)

    product = [{
        'id': 1, 'nombre_producto': 'Café', 'precio': Decimal('10'),
        'stock': 5, 'requiere_inventario': 0,
    }]
    variants = [{'id': 2, 'producto_id': 1, 'precio': 12, 'tamano': 'Grande'}]
    no_selection = _sale_connection(product, variants, method)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: no_selection)
    assert 'Debe seleccionar' in modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, 1, 'seller'
    )[1]

    wrong_variant = _sale_connection(product, variants, method)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: wrong_variant)
    assert 'no pertenece' in modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'variante_id': 3, 'cantidad': 1}], 1, 1, 'seller'
    )[1]

    no_variants = _sale_connection(product, [], method)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: no_variants)
    assert 'no tiene esa variante' in modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'variante_id': 3, 'cantidad': 1}], 1, 1, 'seller'
    )[1]


def test_venta_rechaza_por_stock_efectivo_y_vendedor_o_estado_faltante(monkeypatch):
    product = [{
        'id': 1, 'nombre_producto': 'Café', 'precio': Decimal('10'),
        'stock': 0, 'requiere_inventario': 1,
    }]
    no_stock = _sale_connection(product, [])
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: no_stock)
    result = modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, 1, 'seller', 10
    )
    assert result[2]['productos_sin_stock'][0]['id'] == 1

    available = [{**product[0], 'stock': 5}]
    invalid_cash = _sale_connection(available, [])
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: invalid_cash)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, 1, 'seller', 'bad'
    )[0] is False

    insufficient = _sale_connection(available, [])
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: insufficient)
    assert modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, 1, 'seller', 5
    )[1] == 'El dinero recibido es menor al total de la venta'

    method = {'Id': 2, 'codigo': 'TARJETA', 'tipo_de_pago': 'Tarjeta'}
    missing_seller = connection_with_results(method, available, [], None, None, None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: missing_seller)
    assert modelsVentas.procesar_venta_completa(
        None, None, [{'id': 1, 'cantidad': 1}], 1, 2, 'missing'
    )[1] == 'El vendedor de la sesión ya no está disponible'

    no_state = connection_with_results(
        method, available, [], {'Id': 3}, {'Id': 4}, None
    )
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: no_state)
    assert modelsVentas.procesar_venta_completa(
        None, None, [{'id': 1, 'cantidad': 1}], 1, 2, 'seller'
    )[1] == 'No existe el estado inicial Pendiente'


def test_venta_falla_en_detalle_legado_y_actualizacion_stock(monkeypatch):
    method = {'Id': 2, 'codigo': 'TARJETA', 'tipo_de_pago': 'Tarjeta'}
    product = [{
        'id': 1, 'nombre_producto': 'Café', 'precio': Decimal('10'),
        'stock': 5, 'requiere_inventario': 1,
    }]

    def handler(sql, params, cursor):
        if 'FROM tmetodospago' in sql:
            return method
        if 'FROM tproductos p JOIN tcategorias' in sql:
            return product
        if 'FROM tproductos_variantes pv' in sql:
            return []
        if 'SELECT Id FROM tclientes' in sql:
            return {'Id': 3}
        if 'SELECT Id FROM tusuarios' in sql:
            return {'Id': 4}
        if 'SELECT Id FROM testadosventa' in sql:
            return {'Id': 1}
        if sql.startswith('INSERT INTO tventas'):
            cursor.lastrowid = 8
        if 'FROM information_schema.COLUMNS' in sql:
            return {'total': 0}
        if sql.startswith('UPDATE tproductos SET stock'):
            cursor.rowcount = 0
        return None

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)
    with pytest.raises(RuntimeError, match='reservar el inventario'):
        modelsVentas.procesar_venta_completa(
            'Cliente', '1', [{'id': 1, 'cantidad': 1}], 1, 2, 'seller'
        )
    assert any(
        call[0].startswith('INSERT INTO tdetalleventas (venta_id')
        for call in connection.cursor_instance.calls
    )
    assert connection.rollbacks == 1


def test_venta_con_variante_valida_usa_captura_de_variante(monkeypatch):
    captured = {}

    def handler(sql, params, cursor):
        if 'FROM tmetodospago' in sql:
            return {'Id': 2, 'codigo': 'TARJETA', 'tipo_de_pago': 'Tarjeta'}
        if 'FROM tproductos p JOIN tcategorias' in sql:
            return [{
                'id': 1,
                'nombre_producto': 'Café',
                'precio': Decimal('10.00'),
                'stock': 0,
                'requiere_inventario': 0,
            }]
        if 'FROM tproductos_variantes pv' in sql:
            return [{
                'id': 2,
                'producto_id': 1,
                'precio': Decimal('15.00'),
                'tamano': 'Grande',
            }]
        if 'SELECT Id FROM tclientes' in sql:
            return {'Id': 3}
        if 'SELECT Id FROM tusuarios' in sql:
            return {'Id': 4}
        if 'SELECT Id FROM testadosventa' in sql:
            return {'Id': 1}
        if sql.startswith('INSERT INTO tventas'):
            cursor.lastrowid = 5
        if 'FROM information_schema.COLUMNS' in sql:
            return {'total': 1}
        if sql.startswith('INSERT INTO tdetalleventas'):
            captured['detail'] = params
        return None

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)
    success, _, sale = modelsVentas.procesar_venta_completa(
        'Cliente',
        '1',
        [{'id': 1, 'variante_id': 2, 'cantidad': 1}],
        1,
        2,
        'seller',
    )

    assert success is True
    assert sale['productos'][0]['tamano'] == 'Grande'
    assert captured['detail'][2:5] == (2, 'Café', 'Grande')



@pytest.mark.parametrize('mesa_input,expected_mesa', [
    (None, 'Para llevar'),
    ('', 'Para llevar'),
    ('   ', 'Para llevar'),
    ('Sin mesa', 'Para llevar'),
    ('sin mesa', 'Para llevar'),
    ('Mesa 3', 'Mesa 3'),
    ('Mesa 5', 'Mesa 5'),
])
def test_procesar_venta_normaliza_mesa_para_llevar(monkeypatch, mesa_input, expected_mesa):
    captured = {}

    def handler(sql, params, cursor):
        if 'FROM tmetodospago' in sql:
            return {'Id': 2, 'codigo': 'TARJETA', 'tipo_de_pago': 'Tarjeta'}
        if 'FROM tproductos p JOIN tcategorias' in sql:
            return [{
                'id': 1,
                'nombre_producto': 'Café Americano',
                'precio': Decimal('30.00'),
                'stock': 10,
                'requiere_inventario': 0,
            }]
        if 'FROM tproductos_variantes pv' in sql:
            return []
        if 'SELECT Id FROM tclientes' in sql:
            return {'Id': 10}
        if 'SELECT Id FROM tusuarios' in sql:
            return {'Id': 20}
        if 'SELECT Id FROM testadosventa' in sql:
            return {'Id': 1}
        if sql.startswith('INSERT INTO tventas'):
            captured['sale_params'] = params
            cursor.lastrowid = 100
        if 'FROM information_schema.COLUMNS' in sql:
            return {'total': 1}
        if sql.startswith('INSERT INTO tdetalleventas'):
            return None
        return None

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)

    success, _, _ = modelsVentas.procesar_venta_completa(
        'Cliente Test',
        mesa_input,
        [{'id': 1, 'cantidad': 1}],
        total=1,
        metodo_pago_id=2,
        usuario_actual='vendedor',
    )

    assert success is True
    # In INSERT INTO tventas (cliente_id, vendedor_id, total, metodo_pago_id, numero_mesa, ...)
    assert captured['sale_params'][4] == expected_mesa


def test_obtener_ordenes_pendientes_normaliza_mesa_nula_o_vacia(monkeypatch):
    rows = [
        {'id': 1, 'numero_mesa': None},
        {'id': 2, 'numero_mesa': ''},
        {'id': 3, 'numero_mesa': 'Sin mesa'},
        {'id': 4, 'numero_mesa': 'Mesa 2'},
    ]
    conn = connection_with_results(rows)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: conn)
    ordenes = modelsVentas.obtener_ordenes_pendientes()
    assert ordenes[0]['numero_mesa'] == 'Para llevar'
    assert ordenes[1]['numero_mesa'] == 'Para llevar'
    assert ordenes[2]['numero_mesa'] == 'Para llevar'
    assert ordenes[3]['numero_mesa'] == 'Mesa 2'


def test_obtener_venta_completa_normaliza_mesa_nula_o_vacia(monkeypatch):
    sale = {'Id': 1, 'numero_mesa': 'Sin mesa'}
    details = [{'nombre_producto': 'Café'}]
    conn = connection_with_results(sale, {'total': 1}, details)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: conn)
    venta, _ = modelsVentas.obtener_venta_completa(1)
    assert venta['numero_mesa'] == 'Para llevar'
