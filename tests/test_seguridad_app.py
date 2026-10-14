import base64

import pytest

from werkzeug.security import generate_password_hash


def test_fabrica_lee_clave_secreta_tras_cargar_entorno(monkeypatch):
    from app import create_app

    monkeypatch.setenv('SECRET_KEY', 'configured-after-module-import')

    flask_app = create_app('LOCAL')

    assert flask_app.config['SECRET_KEY'] == 'configured-after-module-import'


def test_fabrica_rechaza_falta_de_clave_secreta(monkeypatch):
    import app as app_module

    monkeypatch.delenv('SECRET_KEY', raising=False)
    monkeypatch.setattr(app_module, 'load_dotenv', lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match='SECRET_KEY es obligatoria'):
        app_module.create_app('LOCAL')


def test_paso_final_recuperacion_redirige_sin_estado_verificado(client):
    response = client.get('/actualizar-contrasena')

    assert response.status_code == 302


def test_acceso_sin_sesion_redirige_a_recuperacion(client):
    response = client.get('/actualizar-contrasena')

    assert '/recuperar-contrasena' in response.headers['Location']


def test_vendedor_no_puede_consultar_otro_usuario(client, authenticated_session):
    authenticated_session(client, role='Vendedor')

    response = client.get('/api/usuarios/1')

    assert response.status_code == 403
    assert response.get_json()['success'] is False


def test_invalid_pdf_signature_is_rejected(client, authenticated_session):
    authenticated_session(client)
    payload = base64.b64encode(b'not-a-pdf').decode('ascii')

    response = client.post('/api/guardar-pdf', json={
        'pdf': payload,
        'nombre': 'archivo.pdf',
        'tipo': 'ticket',
    })

    assert response.status_code == 400
    assert response.get_json()['success'] is False


def test_write_api_rejects_missing_csrf_token(app, client, authenticated_session):
    authenticated_session(client)
    app.config['WTF_CSRF_ENABLED'] = True
    try:
        response = client.post('/api/guardar-pdf', json={
            'pdf': base64.b64encode(b'%PDF-test').decode('ascii'),
            'nombre': 'archivo.pdf',
            'tipo': 'ticket',
        })
    finally:
        app.config['WTF_CSRF_ENABLED'] = False

    assert response.status_code == 400
    assert 'expiró' in response.get_json()['message']


def test_security_headers_are_present(client):
    response = client.get('/')

    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert 'Content-Security-Policy' in response.headers


def test_login_con_credenciales_validas_redirige_a_bienvenida(client, monkeypatch):
    from blueprints import autenticacion_bp

    monkeypatch.setattr(
        autenticacion_bp,
        'buscar_usuario_por_usuario',
        lambda usuario: {
            'Id': 1,
            'activo': True,
            'contrasena': generate_password_hash('Segura123'),
            'rol': 'Administrador',
            'sesion_version': 1,
        },
    )

    response = client.post('/', data={
        'usuario': 'administrador',
        'contrasena': 'Segura123',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/bienvenida')


def test_empleado_vendedor_es_redirigido_desde_panel_admin(
        client, authenticated_session):
    authenticated_session(client, role='Vendedor')

    response = client.get('/corteCaja')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/bienvenida')


def test_plantilla_confirmar_salir_tiene_enlace_cancelar_valido(
        client, authenticated_session):
    authenticated_session(client)

    response = client.get('/confirmar-salir')

    assert response.status_code == 200
    assert 'href="/bienvenida"' in response.get_data(as_text=True)


def test_reporte_pdf_caja_existente_retorna_url_descarga(
        app, client, authenticated_session, tmp_path):
    authenticated_session(client, role='Administrador')
    pdf_name = 'corte_2026-08-01_2026-08-02.pdf'
    (tmp_path / pdf_name).write_bytes(b'%PDF-test')
    app.config['PDF_CORTES_FOLDER'] = str(tmp_path)

    response = client.get('/buscar_pdf_corte/2026-08-01/2026-08-02')

    assert response.status_code == 200
    assert response.get_json() == {
        'success': True,
        'url': f'/api/pdfs/corte/{pdf_name}',
    }


def test_sanitizacion_xss_en_nombre_cliente(client, authenticated_session, monkeypatch):
    from models import modelsVentas
    
    # Mockear la BD para que no intente guardar
    class FakeCursor:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def execute(self, sql, params=None): return 1
        def fetchone(self): return None
        def fetchall(self): return []
        
    class FakeConnection:
        def cursor(self): return FakeCursor()
        def commit(self): pass
        def close(self): pass
        
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: FakeConnection())
    
    authenticated_session(client)
    
    payload = {
        'cliente': '<script>alert("xss")</script>',
        'mesa': '1',
        'productos': [{'id': 10, 'cantidad': 1}],
        'total': '10.00',
        'metodo_pago_id': 1,
        'dinero_recibido': '10.00',
        'cambio': '0.00'
    }
    
    # Intentar procesar una venta con el payload XSS
    response = client.post('/api/ventas/crear', json=payload)
    
    # Incluso si el backend lo acepta o rechaza, la respuesta no debe contener el payload literal
    response_text = response.get_data(as_text=True)
    assert '<script>' not in response_text, "El payload XSS se filtró de vuelta al cliente sin ser escapado o procesado de forma segura"
