import pytest

from models import modelsProductos
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_variant_batch_empty_and_grouped(monkeypatch):
    assert modelsProductos.obtener_variantes_batch([]) == {}

    variants = [
        {'Id': 1, 'producto_id': 10},
        {'Id': 2, 'producto_id': 10},
        {'Id': 3, 'producto_id': 20},
    ]
    connection = connection_with_results(variants)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)

    assert modelsProductos.obtener_variantes_batch([10, 20]) == {
        10: variants[:2],
        20: variants[2:],
    }
    assert connection.closed is True


@pytest.mark.parametrize(
    ('function_name', 'args', 'result'),
    [
        ('obtener_productos', (), [{'Id': 1}]),
        ('obtener_categorias', (), [{'Id': 1, 'categoria': 'Café'}]),
        ('obtener_tamanos', (), [{'Id': 1, 'tamano': 'Chico'}]),
        ('obtener_variantes_por_producto', (10,), [{'Id': 2}]),
    ],
)
def test_product_read_functions_return_rows(
        monkeypatch, function_name, args, result):
    connection = connection_with_results(result)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)

    assert getattr(modelsProductos, function_name)(*args) == result
    assert connection.closed is True


@pytest.mark.parametrize(
    ('function_name', 'args', 'expected'),
    [
        ('obtener_productos', (), []),
        ('obtener_categorias', (), []),
        ('obtener_tamanos', (), []),
        ('obtener_variantes_por_producto', (10,), []),
    ],
)
def test_product_read_functions_handle_errors(
        monkeypatch, function_name, args, expected):
    connection = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)

    assert getattr(modelsProductos, function_name)(*args) == expected
    assert connection.closed is True


def test_add_update_and_delete_variant(monkeypatch):
    added = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: added)
    assert modelsProductos.agregar_variante_producto(1, 2, 30) is True
    assert added.commits == 1

    def update_handler(sql, params, cursor):
        cursor.rowcount = 1

    updated = FakeConnection(update_handler)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: updated)
    assert modelsProductos.actualizar_variante_producto(2, 35) is True

    deleted = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: deleted)
    assert modelsProductos.eliminar_variantes_producto(1) is True


@pytest.mark.parametrize(
    ('function_name', 'args', 'expected'),
    [
        ('agregar_variante_producto', (1, 2, 30), False),
        ('actualizar_variante_producto', (2, 35), False),
        ('eliminar_variantes_producto', (1,), False),
    ],
)
def test_variant_writes_handle_errors(monkeypatch, function_name, args, expected):
    connection = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)
    assert getattr(modelsProductos, function_name)(*args) is expected
    assert connection.closed is True


def test_update_variant_returns_false_when_no_row_changed(monkeypatch):
    connection = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)
    assert modelsProductos.actualizar_variante_producto(2, 35) is False


def test_add_product_returns_generated_id_and_handles_error(monkeypatch):
    def handler(sql, params, cursor):
        cursor.lastrowid = 44

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)
    assert modelsProductos.agregar_producto(
        'Café', 'Descripción', 20, 1, 1, 10, 2, '/image.png'
    ) == (True, 44)
    assert connection.commits == 1

    failed = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: failed)
    assert modelsProductos.agregar_producto(
        'Café', 'Descripción', 20, 1, 1, 10, 2, None
    ) == (False, None)


@pytest.mark.parametrize('image', ['/image.png', None])
def test_update_product_with_and_without_image(monkeypatch, image):
    def handler(sql, params, cursor):
        cursor.rowcount = 1

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)
    result = modelsProductos.actualizar_producto(
        1, 'Café', 'Descripción', 20, 1, 1, 10, 2, image
    )
    assert result == (True, 'Producto actualizado correctamente')
    sql = connection.cursor_instance.calls[0][0]
    assert ('ruta_imagen=%s' in sql) is bool(image)


def test_update_product_handles_no_change_and_error(monkeypatch):
    unchanged = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: unchanged)
    assert modelsProductos.actualizar_producto(
        1, 'Café', 'Descripción', 20, 1, 1, 10, 2
    ) == (False, 'No se realizaron cambios en el producto')

    failed = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: failed)
    success, message = modelsProductos.actualizar_producto(
        1, 'Café', 'Descripción', 20, 1, 1, 10, 2
    )
    assert success is False
    assert message.startswith('Error al actualizar producto:')


def test_soft_delete_product_success_and_error(monkeypatch):
    successful = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: successful)
    assert modelsProductos.eliminar_producto(1) is True
    assert successful.commits == 1

    failed = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: failed)
    assert modelsProductos.eliminar_producto(1) is False
    assert failed.rollbacks == 1


def test_get_product_by_id_with_variants_not_found_and_error(monkeypatch):
    product = {'Id': 1, 'nombre_producto': 'Café'}
    variants = [{'Id': 2}]
    found = connection_with_results(product, variants)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: found)
    assert modelsProductos.obtener_producto_por_id(1) == {
        **product,
        'variantes': variants,
    }

    missing = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: missing)
    assert modelsProductos.obtener_producto_por_id(99) is None

    failed = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: failed)
    assert modelsProductos.obtener_producto_por_id(1) is None
