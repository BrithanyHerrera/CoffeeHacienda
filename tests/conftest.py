import os
from datetime import datetime

import pytest

os.environ['APP_ENV'] = 'TESTING'
os.environ.setdefault('SECRET_KEY', 'testing-only-secret-key')

from app import create_app  # noqa: E402


@pytest.fixture
def app():
    flask_app = create_app('TESTING')
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SESSION_VALIDATION_INTERVAL_SECONDS=3600,
    )
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_session():
    def authenticate(client, role='Vendedor', user_id=1):
        now = datetime.now().isoformat()
        with client.session_transaction() as session:
            session['usuario'] = 'usuario_prueba'
            session['usuario_id'] = user_id
            session['rol'] = role
            session['sesion_version'] = 1
            session['ultima_actividad'] = now
            session['ultima_verificacion_activo'] = now
    return authenticate
