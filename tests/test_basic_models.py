import pytest

from models import modelsHistorial, modelsInventario, modelsLogin, modelsProductosMenu
from tests.db_fakes import FakeConnection, connection_with_results


def test_login_lookup_returns_user_and_closes_connection(monkeypatch):
    user = {'Id': 1, 'rol': 'Administrador'}
    connection = connection_with_results(user)
    monkeypatch.setattr(modelsLogin, 'Conexion_BD', lambda: connection)

    assert modelsLogin.buscar_usuario_por_usuario('admin') == user
    assert connection.closed is True


def test_history_applies_filters_and_pagination(monkeypatch):
    sales = [{'id': 3}, {'id': 2}]
    connection = connection_with_results({'total': 32}, sales)
    monkeypatch.setattr(modelsHistorial, 'Conexion_BD', lambda: connection)

    result, pages, total = modelsHistorial.obtener_historial_ventas(
        filtro_cliente='Ana',
        filtro_vendedor='vendedor',
        fecha_inicio='2026-01-01',
        fecha_fin='2026-01-31',
        pagina=99,
        por_pagina=15,
    )

    assert result == sales
    assert pages == 3
    assert total == 32
    count_sql, count_params = connection.cursor_instance.calls[0]
    assert 'c.nombre LIKE %s' in count_sql
    assert 'u.usuario = %s' in count_sql
    assert count_params == ['%Ana%', 'vendedor', '2026-01-01', '2026-01-31']
    assert connection.cursor_instance.calls[1][1][-2:] == [15, 30]
    assert connection.closed is True


def test_history_returns_safe_empty_result_on_database_error(monkeypatch):
    def handler(sql, params, cursor):
        raise RuntimeError('database error')

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsHistorial, 'Conexion_BD', lambda: connection)

    assert modelsHistorial.obtener_historial_ventas() == ([], 1, 0)
    assert connection.closed is True


def test_payment_methods_return_rows_and_handle_errors(monkeypatch):
    rows = [{'id': 1, 'codigo': 'EFECTIVO'}]
    successful = connection_with_results(rows)
    monkeypatch.setattr(modelsProductosMenu, 'Conexion_BD', lambda: successful)
    assert modelsProductosMenu.obtener_metodos_pago() == rows
    assert successful.closed is True

    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    failed = FakeConnection(fail)
    monkeypatch.setattr(modelsProductosMenu, 'Conexion_BD', lambda: failed)
    assert modelsProductosMenu.obtener_metodos_pago() == []
    assert failed.closed is True


def test_menu_products_group_variants(monkeypatch):
    products = [{'id': 10}, {'id': 20}]
    variants = [
        {'variante_id': 1, 'producto_id': 10, 'tamano': 'Chico', 'precio': 20},
        {'variante_id': 2, 'producto_id': 10, 'tamano': 'Grande', 'precio': 30},
    ]
    connection = connection_with_results(products, variants)
    monkeypatch.setattr(modelsProductosMenu, 'Conexion_BD', lambda: connection)

    result = modelsProductosMenu.obtener_productos_menu()

    assert result[0]['variantes'] == [
        {'variante_id': 1, 'tamano': 'Chico', 'precio': 20},
        {'variante_id': 2, 'tamano': 'Grande', 'precio': 30},
    ]
    assert result[1]['variantes'] == []
    assert connection.closed is True


def test_menu_products_handles_empty_connection_empty_rows_and_error(monkeypatch):
    monkeypatch.setattr(modelsProductosMenu, 'Conexion_BD', lambda: None)
    assert modelsProductosMenu.obtener_productos_menu() == []

    empty = connection_with_results([])
    monkeypatch.setattr(modelsProductosMenu, 'Conexion_BD', lambda: empty)
    assert modelsProductosMenu.obtener_productos_menu() == []
    assert empty.closed is True

    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    failed = FakeConnection(fail)
    monkeypatch.setattr(modelsProductosMenu, 'Conexion_BD', lambda: failed)
    assert modelsProductosMenu.obtener_productos_menu() == []
    assert failed.closed is True


def test_inventory_read_operations(monkeypatch):
    item = {'Id': 10, 'stock': 5}
    by_id = connection_with_results(item)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: by_id)
    assert modelsInventario.obtener_producto_inventario_por_id(10) == item
    assert by_id.closed is True

    rows = [item]
    listed = connection_with_results(rows)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: listed)
    assert modelsInventario.obtener_productos_inventario() == rows

    alerts = connection_with_results({'total': 2}, {'total': 3})
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: alerts)
    assert modelsInventario.contar_alertas_inventario() == {'criticas': 2, 'normales': 3}


@pytest.mark.parametrize(
    ('function_name', 'expected'),
    [
        ('obtener_productos_inventario', []),
        ('contar_alertas_inventario', {'criticas': 0, 'normales': 0}),
    ],
)
def test_inventory_reads_handle_errors(monkeypatch, function_name, expected):
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    connection = FakeConnection(fail)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: connection)
    assert getattr(modelsInventario, function_name)() == expected
    assert connection.closed is True


@pytest.mark.parametrize(
    ('previous', 'new', 'expected_type', 'expected_quantity'),
    [(5, 8, 3, 3), (8, 5, 4, 3)],
)
def test_inventory_update_records_positive_and_negative_adjustments(
        monkeypatch, previous, new, expected_type, expected_quantity):
    captured = []

    def handler(sql, params, cursor):
        if sql.startswith('SELECT stock'):
            return {'stock': previous}
        if sql.startswith('INSERT INTO tmovimientosinventario'):
            captured.append(params)
        return None

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: connection)

    assert modelsInventario.actualizar_stock_producto(10, new, 1, 20) is True
    assert captured[0][1:3] == (expected_quantity, expected_type)
    assert connection.commits == 1


def test_inventory_update_handles_unchanged_missing_and_error(monkeypatch):
    unchanged = connection_with_results({'stock': 5}, None)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: unchanged)
    assert modelsInventario.actualizar_stock_producto(10, 5, 1, 20) is True
    assert len(unchanged.cursor_instance.calls) == 2

    missing = connection_with_results(None)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: missing)
    assert modelsInventario.actualizar_stock_producto(99, 5, 1, 20) is False
    assert missing.rollbacks == 1

    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    failed = FakeConnection(fail)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: failed)
    assert modelsInventario.actualizar_stock_producto(10, 5, 1, 20) is False
    assert failed.rollbacks == 1
