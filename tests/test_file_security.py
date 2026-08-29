import base64
from io import BytesIO

from blueprints import productos_bp
from blueprints.generales_bp import MAX_PDF_BYTES


def _product_form(image):
    return {
        'nombreProducto': 'Producto de archivo',
        'descripcionProducto': 'Prueba',
        'precioProducto': '10.00',
        'stockProducto': '1',
        'stockMinProducto': '1',
        'stockMaxProducto': '10',
        'categoriaProducto': '1',
        'tamano_id': '4',
        'imagenProducto': image,
    }


def test_pdf_over_specific_limit_is_rejected(client, authenticated_session):
    authenticated_session(client)
    payload = base64.b64encode(b'%PDF-' + b'x' * MAX_PDF_BYTES).decode('ascii')

    response = client.post('/api/guardar-pdf', json={
        'pdf': payload,
        'nombre': 'grande.pdf',
        'tipo': 'ticket',
    })

    assert response.status_code == 413
    assert response.get_json()['success'] is False


def test_global_api_request_limit_returns_json(
        app, client, authenticated_session):
    authenticated_session(client)
    original_limit = app.config['MAX_CONTENT_LENGTH']
    app.config['MAX_CONTENT_LENGTH'] = 128
    try:
        response = client.post('/api/guardar-pdf', json={
            'pdf': 'x' * 1024,
            'nombre': 'grande.pdf',
            'tipo': 'ticket',
        })
    finally:
        app.config['MAX_CONTENT_LENGTH'] = original_limit

    assert response.status_code == 413
    assert response.is_json
    assert response.get_json()['success'] is False


def test_pdf_filename_is_generated_inside_configured_folder(
        app, client, authenticated_session, tmp_path):
    authenticated_session(client)
    app.config['PDF_TICKETS_FOLDER'] = str(tmp_path)
    payload = base64.b64encode(b'%PDF-contenido').decode('ascii')

    response = client.post('/api/guardar-pdf', json={
        'pdf': payload,
        'nombre': '../../fuera.pdf',
        'tipo': 'ticket',
    })

    assert response.status_code == 200
    stored_name = response.get_json()['nombre']
    assert '..' not in stored_name
    assert '/' not in stored_name
    assert '\\' not in stored_name
    assert [path.name for path in tmp_path.iterdir()] == [stored_name]


def test_image_over_specific_limit_is_rejected(client, authenticated_session):
    authenticated_session(client, role='Administrador')
    oversized_png = b'\x89PNG\r\n\x1a\n' + b'x' * productos_bp.MAX_IMAGE_BYTES

    response = client.post(
        '/api/productos/guardar',
        data=_product_form((BytesIO(oversized_png), 'grande.png')),
        content_type='multipart/form-data',
    )

    assert response.status_code == 413
    assert response.get_json()['success'] is False


def test_global_image_request_limit_returns_json(
        app, client, authenticated_session):
    authenticated_session(client, role='Administrador')
    original_limit = app.config['MAX_CONTENT_LENGTH']
    app.config['MAX_CONTENT_LENGTH'] = 128
    try:
        response = client.post(
            '/api/productos/guardar',
            data=_product_form((BytesIO(b'\x89PNG\r\n\x1a\n' + b'x' * 1024), 'grande.png')),
            content_type='multipart/form-data',
        )
    finally:
        app.config['MAX_CONTENT_LENGTH'] = original_limit

    assert response.status_code == 413
    assert response.is_json
    assert response.get_json()['success'] is False


def test_fake_image_signature_is_rejected(client, authenticated_session):
    authenticated_session(client, role='Administrador')

    response = client.post(
        '/api/productos/guardar',
        data=_product_form((BytesIO(b'not-a-real-image'), 'falsa.png')),
        content_type='multipart/form-data',
    )

    assert response.status_code == 400
    assert response.get_json()['success'] is False


def test_image_filename_is_generated_inside_configured_folder(
        app, client, authenticated_session, monkeypatch, tmp_path):
    authenticated_session(client, role='Administrador')
    app.config['UPLOAD_FOLDER'] = str(tmp_path)
    monkeypatch.setattr(productos_bp, 'agregar_producto', lambda *args: (True, 99))

    response = client.post(
        '/api/productos/guardar',
        data=_product_form((BytesIO(b'\x89PNG\r\n\x1a\ncontent'), '../../fuera.png')),
        content_type='multipart/form-data',
    )

    assert response.status_code == 200
    stored_files = list(tmp_path.iterdir())
    assert len(stored_files) == 1
    assert stored_files[0].parent == tmp_path
    assert '..' not in stored_files[0].name
