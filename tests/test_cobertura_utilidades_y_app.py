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


def test_tipo_solicitud_y_respuestas_sesion_invalida(app):
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


def test_extensiones_imagen_permitidas():
    assert utils.archivo_permitido('foto.PNG') is True
    assert utils.archivo_permitido('foto.exe') is False
    assert utils.archivo_permitido('sin-extension') is False


def test_login_required_rechaza_sesiones_faltantes_malformadas_y_expiradas(app):
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


def test_login_required_sesiones_recientes_y_validadas_en_bd(app, monkeypatch):
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


def test_login_required_rechaza_estados_usuario_bd_y_errores(app, monkeypatch):
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


def test_admin_required_api_html_y_permitido(app):
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


def test_fortaleza_contrasena_todos_los_resultados():
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


def test_enviar_correo_exito_y_error(app, monkeypatch):
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


def test_fabrica_proxy_procesador_contexto_y_cabeceras_produccion(
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


def test_manejadores_html_csrf_y_solicitud_demasiado_grande(app):
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


def test_manejadores_error_404_500_429():
    from werkzeug.exceptions import InternalServerError, TooManyRequests

    test_app = app_module.create_app('TESTING')
    test_app.add_url_rule(
        '/trigger-500-html',
        'trigger_500_html',
        lambda: (_ for _ in ()).throw(InternalServerError()),
    )
    test_app.add_url_rule(
        '/api/trigger-500',
        'trigger_500_api',
        lambda: (_ for _ in ()).throw(InternalServerError()),
    )
    test_app.add_url_rule(
        '/trigger-429-html',
        'trigger_429_html',
        lambda: (_ for _ in ()).throw(TooManyRequests()),
    )
    test_app.add_url_rule(
        '/api/trigger-429',
        'trigger_429_api',
        lambda: (_ for _ in ()).throw(TooManyRequests()),
    )

    client = test_app.test_client()

    res_404_html = client.get('/ruta-no-existe-para-test')
    assert res_404_html.status_code == 302
    assert res_404_html.headers['Location'] == '/'

    res_404_api = client.get('/api/ruta-no-existe-para-test')
    assert res_404_api.status_code == 404
    assert res_404_api.get_json()['success'] is False

    res_500_api = client.get('/api/trigger-500')
    assert res_500_api.status_code == 500
    assert res_500_api.get_json()['success'] is False

    res_500_html = client.get('/trigger-500-html')
    assert res_500_html.status_code == 500

    res_429_api = client.get('/api/trigger-429')
    assert res_429_api.status_code == 429
    assert res_429_api.get_json()['success'] is False

    res_429_html = client.get('/trigger-429-html')
    assert res_429_html.status_code == 302
    assert res_429_html.headers['Location'] == '/'


def test_punto_entrada_principal_app_ejecuta_limpieza_y_servidor(monkeypatch):
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
