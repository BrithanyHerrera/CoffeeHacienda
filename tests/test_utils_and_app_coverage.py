import runpy
from datetime import datetime, timedelta

from flask import Flask, session
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.proxy_fix import ProxyFix

import app as app_module
import utils
from models import modelsLimpieza
from tests.db_fakes import FakeConnection, connection_with_results


def _valid_session():
    now = datetime.now().isoformat()
    session.update(
        usuario='usuario',
        usuario_id=1,
        rol='Administrador',
        sesion_version=1,
        ultima_actividad=now,
        ultima_verificacion_activo=now,
    )


def test_request_type_and_invalid_session_responses(app):
    with app.test_request_context('/api/test'):
        assert utils._es_solicitud_api() is True
        response, status = utils._sesion_invalida()
        assert status == 401
        assert response.get_json()['success'] is False

    with app.test_request_context('/form', method='POST', json={'x': 1}):
        assert utils._es_solicitud_api() is True

    with app.test_request_context('/page'):
        assert utils._es_solicitud_api() is False
        response = utils._sesion_invalida('Mensaje')
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/')


def test_allowed_image_extensions():
    assert utils.archivo_permitido('foto.PNG') is True
    assert utils.archivo_permitido('foto.exe') is False
    assert utils.archivo_permitido('sin-extension') is False


def test_login_required_rejects_missing_malformed_and_expired_sessions(app):
    protected = utils.login_required(lambda: 'ok')

    with app.test_request_context('/page'):
        assert protected().status_code == 302

    with app.test_request_context('/page'):
        session['usuario'] = 'usuario'
        assert protected().status_code == 302

    with app.test_request_context('/page'):
        _valid_session()
        session['ultima_actividad'] = 'invalid'
        assert protected().status_code == 302

    with app.test_request_context('/page'):
        _valid_session()
        session['ultima_actividad'] = (
            datetime.now() - timedelta(minutes=31)
        ).isoformat()
        assert protected().status_code == 302


def test_login_required_recent_and_database_validated_sessions(app, monkeypatch):
    protected = utils.login_required(lambda: 'ok')

    with app.test_request_context('/page'):
        _valid_session()
        assert protected() == 'ok'

    connection = connection_with_results({'activo': 1, 'sesion_version': 1})
    monkeypatch.setattr(utils, 'Conexion_BD', lambda: connection)
    with app.test_request_context('/page'):
        _valid_session()
        session['ultima_verificacion_activo'] = 'invalid'
        assert protected() == 'ok'
        assert connection.closed is True


def test_login_required_rejects_database_user_states_and_errors(app, monkeypatch):
    protected = utils.login_required(lambda: 'ok')
    for database_user in (
        None,
        {'activo': 0, 'sesion_version': 1},
        {'activo': 1, 'sesion_version': 2},
    ):
        connection = connection_with_results(database_user)
        monkeypatch.setattr(utils, 'Conexion_BD', lambda connection=connection: connection)
        with app.test_request_context('/page'):
            _valid_session()
            session['ultima_verificacion_activo'] = (
                datetime.now() - timedelta(hours=2)
            ).isoformat()
            assert protected().status_code == 302

    monkeypatch.setattr(
        utils,
        'Conexion_BD',
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    with app.test_request_context('/page'):
        _valid_session()
        session['ultima_verificacion_activo'] = 'invalid'
        assert protected().status_code == 302


def test_admin_required_api_html_and_allowed(app):
    protected = utils.admin_required(lambda: 'ok')
    with app.test_request_context('/api/admin'):
        session['rol'] = 'Vendedor'
        response, status = protected()
        assert status == 403
        assert response.get_json()['success'] is False

    with app.test_request_context('/admin'):
        session['rol'] = 'Vendedor'
        assert protected().status_code == 302

    with app.test_request_context('/admin'):
        session['rol'] = 'Administrador'
        assert protected() == 'ok'


def test_password_strength_all_results():
    assert utils.validar_fortaleza_contrasena('Short1') == (
        False, 'La contraseña debe tener al menos 8 caracteres'
    )
    assert utils.validar_fortaleza_contrasena('lowercase1') == (
        False, 'La contraseña debe tener al menos una letra mayúscula'
    )
    assert utils.validar_fortaleza_contrasena('UPPERCASE1') == (
        False, 'La contraseña debe tener al menos una letra minúscula'
    )
    assert utils.validar_fortaleza_contrasena('NoNumbers') == (
        False, 'La contraseña debe tener al menos un número'
    )
    assert utils.validar_fortaleza_contrasena('Valid123') == (True, '')


def test_send_email_success_and_error(app, monkeypatch):
    mail = app.extensions['mail']
    sent = []
    monkeypatch.setattr(mail, 'send', lambda message: sent.append(message))
    with app.app_context():
        assert utils.enviar_correo('to@example.test', 'Subject', 'Body') is True
    assert sent[0].recipients == ['to@example.test']

    monkeypatch.setattr(
        mail,
        'send',
        lambda message: (_ for _ in ()).throw(RuntimeError('mail error')),
    )
    with app.app_context():
        assert utils.enviar_correo('to@example.test', 'Subject', 'Body') is False


def test_factory_proxy_context_processor_and_production_headers(
        monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'secret')
    monkeypatch.setenv('TRUST_PROXY', 'true')
    proxied = app_module.create_app('TESTING')
    assert isinstance(proxied.wsgi_app, ProxyFix)

    processors = proxied.template_context_processors[None]
    inject_alerts = processors[-1]
    monkeypatch.setattr(
        app_module,
        'contar_alertas_inventario',
        lambda: {'criticas': 2, 'normales': 3},
    )
    with proxied.test_request_context('/'):
        session['usuario'] = 'usuario'
        assert inject_alerts() == {'sidebar_alertas_total': 5}

    monkeypatch.setattr(
        app_module,
        'contar_alertas_inventario',
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    with proxied.test_request_context('/'):
        session['usuario'] = 'usuario'
        assert inject_alerts() == {'sidebar_alertas_total': 0}

    monkeypatch.setenv('TRUST_PROXY', 'false')
    production = app_module.create_app('PRODUCTION')
    response = production.test_client().get('/', base_url='https://localhost')
    assert 'max-age=31536000' in response.headers['Strict-Transport-Security']


def test_html_csrf_and_request_too_large_handlers(app):
    endpoint = f'too_large_{id(app)}'
    app.add_url_rule(
        '/too-large-html',
        endpoint,
        lambda: (_ for _ in ()).throw(RequestEntityTooLarge()),
    )
    app.config['WTF_CSRF_ENABLED'] = True
    try:
        response = app.test_client().post('/', data={'usuario': 'x'})
    finally:
        app.config['WTF_CSRF_ENABLED'] = False
    assert response.status_code == 400
    assert response.content_type.startswith('text/html')

    response = app.test_client().get('/too-large-html')
    assert response.status_code == 413
    assert response.get_data(as_text=True) == 'El archivo excede el tamaño permitido.'


def test_app_main_entrypoint_runs_cleanup_and_server(monkeypatch):
    calls = []
    monkeypatch.setattr(
        modelsLimpieza,
        'limpiar_validaciones_expiradas',
        lambda: calls.append('validaciones'),
    )
    monkeypatch.setattr(
        modelsLimpieza,
        'limpiar_codigos_recuperacion_expirados',
        lambda: calls.append('codigos'),
    )
    monkeypatch.setattr(Flask, 'run', lambda self, **kwargs: calls.append('run'))

    runpy.run_module('app', run_name='__main__')

    assert calls == ['validaciones', 'codigos', 'run']
