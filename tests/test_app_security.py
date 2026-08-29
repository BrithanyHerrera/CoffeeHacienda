import base64


def test_password_reset_final_step_redirects_without_verified_state(client):
    response = client.get('/actualizar-contrasena')

    assert response.status_code == 302


def test_password_reset_final_step_returns_to_recovery_start(client):
    response = client.get('/actualizar-contrasena')

    assert '/recuperar-contrasena' in response.headers['Location']


def test_employee_cannot_read_another_user(client, authenticated_session):
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


def test_xss_payload_in_customer_name_is_escaped(client, authenticated_session, monkeypatch):
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
