import base64


def test_password_reset_final_step_requires_verified_state(client):
    response = client.get('/actualizar-contrasena')

    assert response.status_code == 302
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
