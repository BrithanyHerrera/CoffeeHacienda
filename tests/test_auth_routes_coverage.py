import time

import pytest
from flask import session
from werkzeug.security import generate_password_hash

from blueprints import autenticacion_bp


def _recovery_state(**overrides):
    state = {
        'usuario_id': 7,
        'correo': 'persona@example.test',
        'expira_en': int(time.time()) + 600,
        'verificado': False,
        'intentos': 0,
    }
    state.update(overrides)
    return state


@pytest.mark.parametrize(
    'state',
    [
        {'correo': 'persona@example.test', 'expira_en': time.time() + 60},
        {'usuario_id': 7, 'correo': '', 'expira_en': time.time() + 60},
        {'usuario_id': 7, 'correo': None, 'expira_en': time.time() + 60},
    ],
)
def test_recovery_state_rejects_incomplete_or_invalid_values(app, state):
    with app.test_request_context('/'):
        session[autenticacion_bp._ESTADO_RECUPERACION] = state
        assert autenticacion_bp._obtener_estado_recuperacion() is None
        assert autenticacion_bp._ESTADO_RECUPERACION not in session


@pytest.mark.parametrize('case', ['empty', 'missing', 'inactive', 'wrong-password'])
def test_login_rejects_invalid_credentials(client, monkeypatch, case):
    user = {
        'Id': 1,
        'activo': True,
        'contrasena': generate_password_hash('Correcta123'),
        'rol': 'Vendedor',
        'sesion_version': 1,
    }
    if case == 'missing':
        result = None
    else:
        result = user
    if case == 'inactive':
        user['activo'] = False

    monkeypatch.setattr(
        autenticacion_bp,
        'buscar_usuario_por_usuario',
        lambda username: result,
    )
    payload = {
        'usuario': '' if case == 'empty' else 'persona',
        'contrasena': '' if case == 'empty' else 'Incorrecta123',
    }
    response = client.post('/', data=payload)
    assert response.status_code == 200


def test_logout_clears_session(client, authenticated_session):
    authenticated_session(client)
    response = client.get('/salir')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
    with client.session_transaction() as current_session:
        assert 'usuario' not in current_session


def test_recovery_get_and_empty_or_unknown_email(client, monkeypatch):
    assert client.get('/recuperar-contrasena').status_code == 200
    assert client.post('/recuperar-contrasena', data={'correo': ''}).status_code == 200

    monkeypatch.setattr(
        autenticacion_bp,
        'obtener_usuario_por_correo',
        lambda email: None,
    )
    response = client.post(
        '/recuperar-contrasena', data={'correo': 'nadie@example.test'}
    )
    assert response.status_code == 200


def test_recovery_rejects_code_storage_failure(client, monkeypatch):
    monkeypatch.setattr(
        autenticacion_bp,
        'obtener_usuario_por_correo',
        lambda email: {'Id': 7},
    )
    monkeypatch.setattr(autenticacion_bp, 'generar_codigo', lambda: '123456')
    monkeypatch.setattr(
        autenticacion_bp, 'guardar_codigo_recuperacion', lambda *args: False
    )
    response = client.post(
        '/recuperar-contrasena', data={'correo': 'persona@example.test'}
    )
    assert response.status_code == 200


@pytest.mark.parametrize('email_sent', [False, True])
def test_recovery_handles_email_delivery(client, monkeypatch, email_sent):
    deleted = []
    monkeypatch.setattr(
        autenticacion_bp,
        'obtener_usuario_por_correo',
        lambda email: {'Id': 7},
    )
    monkeypatch.setattr(autenticacion_bp, 'generar_codigo', lambda: '123456')
    monkeypatch.setattr(
        autenticacion_bp, 'guardar_codigo_recuperacion', lambda *args: True
    )
    monkeypatch.setattr(
        autenticacion_bp, 'enviar_correo', lambda *args: email_sent
    )
    monkeypatch.setattr(
        autenticacion_bp,
        'eliminar_codigos_recuperacion',
        lambda user_id: deleted.append(user_id),
    )

    response = client.post(
        '/recuperar-contrasena', data={'correo': 'Persona@Example.Test'}
    )
    if email_sent:
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/verificar-codigo')
        with client.session_transaction() as current_session:
            state = current_session[autenticacion_bp._ESTADO_RECUPERACION]
            assert state['correo'] == 'persona@example.test'
            assert state['intentos'] == 0
    else:
        assert response.status_code == 200
        assert deleted == [7]


def test_verify_code_requires_state_and_redirects_verified_state(client):
    response = client.get('/verificar-codigo')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/recuperar-contrasena')

    with client.session_transaction() as current_session:
        current_session[autenticacion_bp._ESTADO_RECUPERACION] = _recovery_state(
            verificado=True,
            permiso_cambio='Abcdef1234',
        )
    response = client.get('/verificar-codigo')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/actualizar-contrasena')


def test_verify_code_consumes_valid_code(client, monkeypatch):
    with client.session_transaction() as current_session:
        current_session[autenticacion_bp._ESTADO_RECUPERACION] = _recovery_state()
    monkeypatch.setattr(
        autenticacion_bp,
        'verificar_codigo_recuperacion',
        lambda *args, **kwargs: True,
    )
    monkeypatch.setattr(
        autenticacion_bp, '_generar_permiso_cambio', lambda: 'Abcdef1234'
    )

    response = client.post('/verificar-codigo', data={'codigo': '123456'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/actualizar-contrasena')
    with client.session_transaction() as current_session:
        state = current_session[autenticacion_bp._ESTADO_RECUPERACION]
        assert state['verificado'] is True
        assert state['permiso_cambio'] == 'Abcdef1234'
        assert 'intentos' not in state


def _set_verified_recovery(client, **overrides):
    with client.session_transaction() as current_session:
        current_session[autenticacion_bp._ESTADO_RECUPERACION] = _recovery_state(
            verificado=True,
            permiso_cambio='Abcdef1234',
            **overrides,
        )


def test_update_password_requires_verified_permission(client):
    with client.session_transaction() as current_session:
        current_session[autenticacion_bp._ESTADO_RECUPERACION] = _recovery_state()
    response = client.get('/actualizar-contrasena')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/verificar-codigo')


@pytest.mark.parametrize('user', [None, {'Id': 8, 'contrasena': 'hash'}])
def test_update_password_rejects_changed_user(client, monkeypatch, user):
    _set_verified_recovery(client)
    monkeypatch.setattr(
        autenticacion_bp, 'obtener_usuario_por_correo', lambda email: user
    )
    response = client.get('/actualizar-contrasena')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/recuperar-contrasena')
    with client.session_transaction() as current_session:
        assert autenticacion_bp._ESTADO_RECUPERACION not in current_session


def _valid_recovery_user():
    return {
        'Id': 7,
        'contrasena': generate_password_hash('Anterior123'),
    }


def test_update_password_get_and_validation_errors(client, monkeypatch):
    _set_verified_recovery(client)
    monkeypatch.setattr(
        autenticacion_bp,
        'obtener_usuario_por_correo',
        lambda email: _valid_recovery_user(),
    )
    assert client.get('/actualizar-contrasena').status_code == 200

    response = client.post('/actualizar-contrasena', data={
        'nueva_contrasena': 'débil',
        'confirmar_contrasena': 'débil',
    })
    assert response.status_code == 200


@pytest.mark.parametrize(
    ('password', 'confirmation'),
    [
        ('Anterior123', 'Anterior123'),
        ('NuevaSegura123', 'Diferente123'),
    ],
)
def test_update_password_rejects_reuse_and_mismatch(
        client, monkeypatch, password, confirmation):
    _set_verified_recovery(client)
    user = _valid_recovery_user()
    monkeypatch.setattr(
        autenticacion_bp, 'obtener_usuario_por_correo', lambda email: user
    )
    response = client.post('/actualizar-contrasena', data={
        'nueva_contrasena': password,
        'confirmar_contrasena': confirmation,
    })
    assert response.status_code == 200


@pytest.mark.parametrize('updated', [True, False])
def test_update_password_final_result(client, monkeypatch, updated):
    _set_verified_recovery(client)
    monkeypatch.setattr(
        autenticacion_bp,
        'obtener_usuario_por_correo',
        lambda email: _valid_recovery_user(),
    )
    captured = []
    monkeypatch.setattr(
        autenticacion_bp,
        'actualizar_contrasena_por_codigo',
        lambda *args: captured.append(args) or updated,
    )

    response = client.post('/actualizar-contrasena', data={
        'nueva_contrasena': 'NuevaSegura123',
        'confirmar_contrasena': 'NuevaSegura123',
    })
    assert response.status_code == 302
    expected_path = '/' if updated else '/recuperar-contrasena'
    assert response.headers['Location'].endswith(expected_path)
    assert len(captured) == 1
    assert captured[0][2] == 'Abcdef1234'
    with client.session_transaction() as current_session:
        assert autenticacion_bp._ESTADO_RECUPERACION not in current_session
