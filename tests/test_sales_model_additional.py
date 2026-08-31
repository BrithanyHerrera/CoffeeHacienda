from decimal import Decimal

import pytest

from models import modelsVentas
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_sale_numeric_helpers_cover_strings_and_invalid_money():
    assert modelsVentas._entero_positivo(' 2 ', 'Campo') == 2
    for value in (True, -1, 'NaN', 'Infinity'):
        with pytest.raises(ValueError):
            modelsVentas._monto_no_negativo(value, 'Monto')


def test_pending_orders_success_and_error(monkeypatch):
    rows = [{'id': 1}]
    successful = connection_with_results(rows)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: successful)
    assert modelsVentas.obtener_ordenes_pendientes() == rows

    failed = _failing_connection()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: failed)
    assert modelsVentas.obtener_ordenes_pendientes() == []


def test_update_order_state_branches(monkeypatch):
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


def test_order_details_new_old_schema_and_error(monkeypatch):
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


def test_get_order_state_and_sellers(monkeypatch):
    state = {'estado_id': 1}
    state_connection = connection_with_results(state)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: state_connection)
    assert modelsVentas.obtener_estado_orden(1) == state

    sellers = [{'usuario': 'ana'}]
    seller_connection = connection_with_results(sellers)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: seller_connection)
    assert modelsVentas.obtener_vendedores_activos() == sellers


@pytest.mark.parametrize('reason', ['', 'x', None, 'x' * 256])
def test_cancel_order_rejects_invalid_reason(reason):
    assert modelsVentas.cancelar_orden(1, 1, reason) is False


@pytest.mark.parametrize('user_id', [None, 0, True, 'abc'])
def test_cancel_order_rejects_invalid_user(user_id):
    assert modelsVentas.cancelar_orden(1, user_id, 'Motivo válido') is False


def test_cancel_order_missing_already_cancelled_and_invalid_state(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: missing)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False

    cancelled = connection_with_results({'estado_id': 3})
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: cancelled)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is True

    completed = connection_with_results({'estado_id': 4})
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: completed)
    assert modelsVentas.cancelar_orden(1, 1, 'Motivo válido') is False


def test_cancel_order_rolls_back_when_stock_or_sale_update_fails(monkeypatch):
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


def test_delete_order_alias(monkeypatch):
    monkeypatch.setattr(modelsVentas, 'cancelar_orden', lambda *args: 'resultado')
    assert modelsVentas.eliminar_orden(1, 2, 'Motivo') == 'resultado'


def test_get_complete_sale_missing_new_old_and_error(monkeypatch):
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
def test_sale_rejects_invalid_product_collection(monkeypatch, products):
    connection = connection_with_results()
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)
    result = modelsVentas.procesar_venta_completa(
        'Cliente', '1', products, 1, 1, 'seller'
    )
    assert result[0] is False


def test_sale_rejects_too_many_items_invalid_method_and_unknown_method(monkeypatch):
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


def test_sale_rejects_non_dict_missing_product_and_variant_mismatches(monkeypatch):
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


def test_sale_rejects_stock_cash_and_missing_seller_or_state(monkeypatch):
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


def test_sale_legacy_detail_and_stock_update_failure(monkeypatch):
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


def test_sale_with_valid_variant_uses_variant_snapshot(monkeypatch):
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
