from io import BytesIO

import pytest

from blueprints import productos_bp


def _product_form(**overrides):
    data = {
        'nombreProducto': 'Café de prueba',
        'descripcionProducto': 'Descripción',
        'precioProducto': '45.50',
        'stockProducto': '10',
        'stockMinProducto': '2',
        'stockMaxProducto': '20',
        'categoriaProducto': '1',
        'tamano_id': '4',
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize('with_products', [False, True])
def test_product_management_page(
        client, authenticated_session, monkeypatch, with_products):
    authenticated_session(client, role='Administrador')
    products = [{'Id': 1, 'nombre': 'Café'}] if with_products else []
    monkeypatch.setattr(productos_bp, 'obtener_productos', lambda: products)
    monkeypatch.setattr(productos_bp, 'obtener_categorias', lambda: [])
    monkeypatch.setattr(productos_bp, 'obtener_tamanos', lambda: [])
    monkeypatch.setattr(
        productos_bp,
        'obtener_variantes_batch',
        lambda ids: {1: [{'Id': 2}]},
    )
    response = client.get('/gestionProductos')
    assert response.status_code == 200
    if with_products:
        assert products[0]['variantes'] == [{'Id': 2}]


@pytest.mark.parametrize(
    ('path', 'attribute', 'key'),
    [
        ('/api/categorias', 'obtener_categorias', 'categorias'),
        ('/api/tamanos', 'obtener_tamanos', 'tamanos'),
    ],
)
def test_product_catalog_endpoints_success_and_error(
        client, authenticated_session, monkeypatch, path, attribute, key):
    authenticated_session(client)
    monkeypatch.setattr(productos_bp, attribute, lambda: [{'Id': 1}])
    response = client.get(path)
    assert response.get_json()[key] == [{'Id': 1}]

    monkeypatch.setattr(
        productos_bp,
        attribute,
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get(path).status_code == 500


@pytest.mark.parametrize(
    'form',
    [
        {},
        _product_form(nombreProducto=''),
        _product_form(descripcionProducto='x' * 2001),
        _product_form(precioProducto='-1'),
        _product_form(stockMinProducto='21', stockMaxProducto='20'),
    ],
)
def test_save_product_rejects_invalid_data(
        client, authenticated_session, form):
    authenticated_session(client, role='Administrador')
    response = client.post('/api/productos/guardar', data=form)
    assert response.status_code == 400
    assert response.get_json()['success'] is False


def test_save_product_rejects_disallowed_image_extension(
        client, authenticated_session):
    authenticated_session(client, role='Administrador')
    form = _product_form()
    form['imagenProducto'] = (BytesIO(b'not-an-image'), 'archivo.txt')
    response = client.post(
        '/api/productos/guardar', data=form, content_type='multipart/form-data'
    )
    assert response.status_code == 400


@pytest.mark.parametrize('size_id', ['2', '4'])
def test_update_product_keeps_image_and_updates_variants(
        client, authenticated_session, monkeypatch, size_id):
    authenticated_session(client, role='Administrador')
    calls = []
    monkeypatch.setattr(
        productos_bp,
        'obtener_producto_por_id',
        lambda product_id: {'ruta_imagen': '/static/images/productos/anterior.png'},
    )
    monkeypatch.setattr(
        productos_bp,
        'actualizar_producto',
        lambda *args: (True, 'Producto actualizado'),
    )
    monkeypatch.setattr(
        productos_bp,
        'eliminar_variantes_producto',
        lambda product_id: calls.append(('delete', product_id)),
    )
    monkeypatch.setattr(
        productos_bp,
        'agregar_variante_producto',
        lambda *args: calls.append(('add',) + args) or True,
    )

    response = client.post(
        '/api/productos/guardar',
        data=_product_form(id='9', tamano_id=size_id),
    )
    assert response.get_json()['success'] is True
    assert calls[0] == ('delete', '9')
    if size_id == '2':
        assert calls[1][0] == 'add'
    else:
        assert len(calls) == 1


@pytest.mark.parametrize('created', [False, True])
def test_create_product_result_and_optional_variant(
        client, authenticated_session, monkeypatch, created):
    authenticated_session(client, role='Administrador')
    variants = []
    monkeypatch.setattr(
        productos_bp, 'agregar_producto', lambda *args: (created, 12)
    )
    monkeypatch.setattr(
        productos_bp,
        'agregar_variante_producto',
        lambda *args: variants.append(args) or True,
    )
    response = client.post(
        '/api/productos/guardar',
        data=_product_form(tamano_id='2'),
    )
    assert response.get_json()['success'] is created
    assert bool(variants) is created


def test_save_product_handles_unexpected_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        productos_bp,
        'agregar_producto',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/productos/guardar', data=_product_form())
    assert response.status_code == 500


@pytest.mark.parametrize('deleted', [False, True])
def test_delete_product_results(
        client, authenticated_session, monkeypatch, deleted):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(productos_bp, 'eliminar_producto', lambda product_id: deleted)
    response = client.post('/api/productos/eliminar', json={'id': 4})
    assert response.get_json()['success'] is deleted


def test_delete_product_handles_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        productos_bp,
        'eliminar_producto',
        lambda product_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.post('/api/productos/eliminar', json={'id': 4}).status_code == 500


@pytest.mark.parametrize(
    ('payload', 'expected_status'),
    [
        ({}, 400),
        ({'producto_id': -1, 'tamano_id': 1, 'precio': 10}, 400),
        ({'producto_id': 1, 'tamano_id': 2, 'precio': 10}, 200),
    ],
)
def test_save_product_variant_validation_and_success(
        client, authenticated_session, monkeypatch, payload, expected_status):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        productos_bp, 'agregar_variante_producto', lambda *args: True
    )
    response = client.post('/api/productos/variantes', json=payload)
    assert response.status_code == expected_status


def test_save_product_variant_handles_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        productos_bp,
        'agregar_variante_producto',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/productos/variantes', json={
        'producto_id': 1,
        'tamano_id': 2,
        'precio': 10,
    })
    assert response.status_code == 500


def test_get_product_variants_success_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        productos_bp, 'obtener_variantes_por_producto', lambda product_id: []
    )
    assert client.get('/api/productos/variantes/1').status_code == 200
    monkeypatch.setattr(
        productos_bp,
        'obtener_variantes_por_producto',
        lambda product_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/productos/variantes/1').status_code == 500


def test_get_product_found_missing_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        productos_bp, 'obtener_producto_por_id', lambda product_id: {'Id': product_id}
    )
    monkeypatch.setattr(
        productos_bp, 'obtener_variantes_por_producto', lambda product_id: []
    )
    assert client.get('/api/productos/1').get_json()['success'] is True

    monkeypatch.setattr(productos_bp, 'obtener_producto_por_id', lambda product_id: None)
    assert client.get('/api/productos/1').get_json()['success'] is False

    monkeypatch.setattr(
        productos_bp,
        'obtener_producto_por_id',
        lambda product_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/productos/1').status_code == 500


def test_get_category_found_missing_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        productos_bp, 'obtener_categorias', lambda: [{'Id': 1, 'nombre': 'Café'}]
    )
    assert client.get('/api/categorias/1').get_json()['success'] is True
    assert client.get('/api/categorias/2').get_json()['success'] is False

    monkeypatch.setattr(
        productos_bp,
        'obtener_categorias',
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/categorias/1').status_code == 500
