import pytest

from models import modelsProductos
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_lote_variantes_vacio_y_agrupado(monkeypatch):
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
def test_funciones_lectura_producto_retornan_filas(
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
def test_funciones_lectura_producto_manejan_errores(
        monkeypatch, function_name, args, expected):
    connection = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)

    assert getattr(modelsProductos, function_name)(*args) == expected
    assert connection.closed is True


def test_agregar_actualizar_y_eliminar_variante(monkeypatch):
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
def test_escrituras_variante_manejan_errores(monkeypatch, function_name, args, expected):
    connection = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)
    assert getattr(modelsProductos, function_name)(*args) is expected
    assert connection.closed is True


def test_actualizar_variante_retorna_falso_cuando_no_cambia_fila(monkeypatch):
    connection = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: connection)
    assert modelsProductos.actualizar_variante_producto(2, 35) is False


def test_agregar_producto_retorna_id_generado_y_maneja_error(monkeypatch):
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
def test_actualizar_producto_con_y_sin_imagen(monkeypatch, image):
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


def test_actualizar_producto_maneja_sin_cambios_y_error(monkeypatch):
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


def test_eliminacion_logica_producto_exito_y_error(monkeypatch):
    successful = connection_with_results(None)
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: successful)
    assert modelsProductos.eliminar_producto(1) is True
    assert successful.commits == 1

    failed = _failing_connection()
    monkeypatch.setattr(modelsProductos, 'Conexion_BD', lambda: failed)
    assert modelsProductos.eliminar_producto(1) is False
    assert failed.rollbacks == 1


def test_obtener_producto_por_id_con_variantes_no_encontrado_y_error(monkeypatch):
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
