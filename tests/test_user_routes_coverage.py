import pytest

from blueprints import usuarios_bp


def _user_payload(**overrides):
    payload = {
        'nombre': 'Persona',
        'contrasena': 'Segura123',
        'correo': 'persona@example.test',
        'tipoPrivilegio': 2,
    }
    payload.update(overrides)
    return payload


def test_user_management_page(client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(usuarios_bp, 'obtener_usuarios_activos', lambda: [])
    monkeypatch.setattr(usuarios_bp, 'obtener_usuarios_inactivos', lambda: [])
    monkeypatch.setattr(usuarios_bp, 'obtener_roles', lambda: [])
    assert client.get('/gestionUsuarios').status_code == 200


def test_save_user_rejects_missing_fields(client, authenticated_session):
    authenticated_session(client, role='Administrador')
    response = client.post('/api/usuarios/guardar', json={})
    assert response.get_json()['success'] is False


def test_update_user_missing_and_weak_password(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(usuarios_bp, 'obtener_usuario_por_id', lambda user_id: None)
    response = client.post(
        '/api/usuarios/guardar', json=_user_payload(id=3)
    )
    assert response.status_code == 404

    monkeypatch.setattr(
        usuarios_bp,
        'obtener_usuario_por_id',
        lambda user_id: {'Id': user_id, 'correo': 'persona@example.test'},
    )
    response = client.post(
        '/api/usuarios/guardar',
        json=_user_payload(id=3, contrasena='débil'),
    )
    assert response.get_json()['success'] is False


@pytest.mark.parametrize(
    ('updated', 'validation_id', 'requires_validation'),
    [
        (False, None, False),
        (True, None, False),
        (True, 44, True),
    ],
)
def test_update_user_with_changed_email(
        client, authenticated_session, monkeypatch,
        updated, validation_id, requires_validation):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        usuarios_bp,
        'obtener_usuario_por_id',
        lambda user_id: {'Id': user_id, 'correo': 'anterior@example.test'},
    )
    monkeypatch.setattr(
        usuarios_bp,
        'actualizar_usuario',
        lambda *args: (updated, 'resultado'),
    )
    monkeypatch.setattr(usuarios_bp, 'generar_codigo', lambda: '123456')
    monkeypatch.setattr(
        usuarios_bp,
        'guardar_cambio_correo_pendiente',
        lambda *args: validation_id,
    )
    emails = []
    monkeypatch.setattr(
        usuarios_bp,
        'enviar_correo',
        lambda *args: emails.append(args) or True,
    )

    response = client.post(
        '/api/usuarios/guardar',
        json=_user_payload(id=3, correo='nuevo@example.test'),
    )
    body = response.get_json()
    assert body['success'] is updated
    assert body.get('require_validation', False) is requires_validation
    assert bool(emails) is requires_validation
    if requires_validation:
        with client.session_transaction() as current_session:
            assert current_session[usuarios_bp.VALIDACION_ID_SESION] == 44
            assert current_session[usuarios_bp.VALIDACION_CORREO_SESION] == 'nuevo@example.test'


def test_update_user_without_email_change(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        usuarios_bp,
        'obtener_usuario_por_id',
        lambda user_id: {'Id': user_id, 'correo': 'persona@example.test'},
    )
    monkeypatch.setattr(
        usuarios_bp,
        'actualizar_usuario',
        lambda *args: (True, 'Usuario actualizado'),
    )
    response = client.post(
        '/api/usuarios/guardar',
        json=_user_payload(id=3, contrasena=''),
    )
    assert response.get_json()['success'] is True


@pytest.mark.parametrize(
    ('password', 'saved', 'expected_success'),
    [
        ('', True, False),
        ('débil', True, False),
        ('Segura123', False, False),
        ('Segura123', True, True),
    ],
)
def test_create_user_results(
        client, authenticated_session, monkeypatch,
        password, saved, expected_success):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        usuarios_bp,
        'guardar_usuario_pendiente',
        lambda *args: (
            saved,
            'resultado',
            {'id': 51, 'codigo': '123456'} if saved else None,
        ),
    )
    monkeypatch.setattr(usuarios_bp, 'enviar_correo', lambda *args: True)
    response = client.post(
        '/api/usuarios/guardar',
        json=_user_payload(contrasena=password),
    )
    assert response.get_json()['success'] is expected_success
    if expected_success:
        assert response.get_json()['require_validation'] is True


def test_save_user_handles_error(client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        usuarios_bp,
        'guardar_usuario_pendiente',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/usuarios/guardar', json=_user_payload())
    assert response.status_code == 500


def test_get_user_found_missing_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        usuarios_bp,
        'obtener_usuario_por_id',
        lambda user_id: {
            'Id': user_id,
            'usuario': 'Persona',
            'correo': 'persona@example.test',
            'rol': 'Vendedor',
            'contrasena': 'never-expose',
        },
    )
    body = client.get('/api/usuarios/3').get_json()
    assert body['success'] is True
    assert 'contrasena' not in body['usuario']

    monkeypatch.setattr(usuarios_bp, 'obtener_usuario_por_id', lambda user_id: None)
    assert client.get('/api/usuarios/3').get_json()['success'] is False

    monkeypatch.setattr(
        usuarios_bp,
        'obtener_usuario_por_id',
        lambda user_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/usuarios/3').status_code == 500


@pytest.mark.parametrize(
    ('path', 'attribute', 'result'),
    [
        ('/gestionUsuarios/eliminar/3', 'desactivar_usuario', (True, 'ok')),
        ('/gestionUsuarios/activar/3', 'reactivar_usuario', True),
        ('/gestionUsuarios/activar/3', 'reactivar_usuario', False),
    ],
)
def test_user_activation_routes(
        client, authenticated_session, monkeypatch, path, attribute, result):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(usuarios_bp, attribute, lambda user_id: result)
    assert client.post(path).status_code == 200


@pytest.mark.parametrize(
    ('path', 'attribute'),
    [
        ('/gestionUsuarios/eliminar/3', 'desactivar_usuario'),
        ('/gestionUsuarios/activar/3', 'reactivar_usuario'),
    ],
)
def test_user_activation_routes_handle_errors(
        client, authenticated_session, monkeypatch, path, attribute):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        usuarios_bp,
        attribute,
        lambda user_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.post(path).status_code == 500


def test_user_validation_page(client):
    response = client.get('/validar-usuario?email=persona@example.test')
    assert response.status_code == 200


def test_validate_user_code_missing_success_and_error(client, monkeypatch):
    assert client.post('/api/usuarios/validar', json={}).get_json()['success'] is False
    with client.session_transaction() as current_session:
        current_session[usuarios_bp.VALIDACION_ID_SESION] = 7
        current_session[usuarios_bp.VALIDACION_CORREO_SESION] = 'persona@example.test'
    monkeypatch.setattr(
        usuarios_bp, 'validar_codigo_usuario', lambda *args: (True, 'ok')
    )
    response = client.post('/api/usuarios/validar', json={
        'correo': 'persona@example.test',
        'codigo': '123456',
    })
    assert response.get_json()['success'] is True
    with client.session_transaction() as current_session:
        assert usuarios_bp.VALIDACION_ID_SESION not in current_session


def test_validate_user_code_handles_error(client, monkeypatch):
    monkeypatch.setattr(
        usuarios_bp,
        'validar_codigo_usuario',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/usuarios/validar', json={
        'correo': 'persona@example.test',
        'codigo': '123456',
    })
    assert response.status_code == 500


@pytest.mark.parametrize(
    ('model_result', 'email_sent', 'expected_success'),
    [
        ((False, 'no disponible', None), True, False),
        ((True, 'ok', '123456'), False, False),
        ((True, 'ok', '123456'), True, True),
    ],
)
def test_resend_validation_code_results(
        client, monkeypatch, model_result, email_sent, expected_success):
    monkeypatch.setattr(
        usuarios_bp, 'reenviar_codigo_validacion', lambda email: model_result
    )
    monkeypatch.setattr(
        usuarios_bp, 'enviar_correo', lambda *args: email_sent
    )
    response = client.post('/api/usuarios/reenviar-codigo', json={
        'correo': 'persona@example.test',
    })
    assert response.get_json()['success'] is expected_success


def test_resend_validation_code_missing_and_error(client, monkeypatch):
    assert client.post('/api/usuarios/reenviar-codigo', json={}).status_code == 200
    monkeypatch.setattr(
        usuarios_bp,
        'reenviar_codigo_validacion',
        lambda email: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/usuarios/reenviar-codigo', json={
        'correo': 'persona@example.test',
    })
    assert response.status_code == 500


def _bind_email_validation(client, email='anterior@example.test'):
    with client.session_transaction() as current_session:
        current_session[usuarios_bp.VALIDACION_ID_SESION] = 71
        current_session[usuarios_bp.VALIDACION_CORREO_SESION] = email


def test_update_validation_email_requires_data_and_session(
        client, authenticated_session):
    authenticated_session(client, role='Administrador')
    assert client.post('/api/usuarios/actualizar-correo', json={}).status_code == 200
    response = client.post('/api/usuarios/actualizar-correo', json={
        'correo_anterior': 'anterior@example.test',
        'correo_nuevo': 'nuevo@example.test',
    })
    assert response.status_code == 403


def test_update_validation_email_rejects_stale_request(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    _bind_email_validation(client)
    monkeypatch.setattr(usuarios_bp, 'obtener_validacion_pendiente', lambda key: None)
    response = client.post('/api/usuarios/actualizar-correo', json={
        'correo_anterior': 'anterior@example.test',
        'correo_nuevo': 'nuevo@example.test',
    })
    assert response.status_code == 403


@pytest.mark.parametrize('duplicate', [False, True])
def test_update_validation_email_rejects_same_or_duplicate(
        client, authenticated_session, monkeypatch, duplicate):
    authenticated_session(client, role='Administrador')
    _bind_email_validation(client)
    monkeypatch.setattr(
        usuarios_bp,
        'obtener_validacion_pendiente',
        lambda key: {'correo': 'anterior@example.test'},
    )
    monkeypatch.setattr(
        usuarios_bp, 'correo_existe_en_usuarios', lambda email: duplicate
    )
    new_email = 'nuevo@example.test' if duplicate else 'anterior@example.test'
    response = client.post('/api/usuarios/actualizar-correo', json={
        'correo_anterior': 'anterior@example.test',
        'correo_nuevo': new_email,
    })
    assert response.get_json()['success'] is False


@pytest.mark.parametrize(
    ('updated', 'email_sent', 'expected_status', 'expected_success'),
    [
        (False, True, 409, False),
        (True, False, 200, False),
        (True, True, 200, True),
    ],
)
def test_update_validation_email_results(
        client, authenticated_session, monkeypatch,
        updated, email_sent, expected_status, expected_success):
    authenticated_session(client, role='Administrador')
    _bind_email_validation(client)
    monkeypatch.setattr(
        usuarios_bp,
        'obtener_validacion_pendiente',
        lambda key: {'correo': 'anterior@example.test'},
    )
    monkeypatch.setattr(
        usuarios_bp, 'correo_existe_en_usuarios', lambda email: False
    )
    monkeypatch.setattr(usuarios_bp, 'generar_codigo', lambda: '123456')
    monkeypatch.setattr(
        usuarios_bp,
        'actualizar_correo_validacion',
        lambda *args: updated,
    )
    monkeypatch.setattr(
        usuarios_bp, 'enviar_correo', lambda *args: email_sent
    )
    response = client.post('/api/usuarios/actualizar-correo', json={
        'correo_anterior': 'anterior@example.test',
        'correo_nuevo': 'nuevo@example.test',
    })
    assert response.status_code == expected_status
    assert response.get_json()['success'] is expected_success


def test_update_validation_email_handles_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    _bind_email_validation(client)
    monkeypatch.setattr(
        usuarios_bp,
        'obtener_validacion_pendiente',
        lambda key: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/usuarios/actualizar-correo', json={
        'correo_anterior': 'anterior@example.test',
        'correo_nuevo': 'nuevo@example.test',
    })
    assert response.status_code == 500
