import time

from blueprints import autenticacion_bp
from models import modelsRecuperacion


class RecoveryCursor:
    def __init__(self, state):
        self.state = state
        self.result = None
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, params=None):
        normalized = ' '.join(sql.split())
        self.rowcount = 0
        if normalized.startswith('SELECT Id, codigo FROM tcodigosrecuperacion'):
            self.result = (
                {'Id': 1, 'codigo': self.state['codigo']}
                if self.state.get('vigente') else None
            )
        elif normalized.startswith('UPDATE tcodigosrecuperacion SET codigo'):
            self.state['codigo'] = params[0]
            self.rowcount = 1
            self.result = None
        else:
            raise AssertionError(f'Consulta inesperada: {normalized}')

    def fetchone(self):
        return self.result


class RecoveryConnection:
    def __init__(self, state):
        self.cursor_instance = RecoveryCursor(state)
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


def _recovery_state(**overrides):
    state = {
        'usuario_id': 7,
        'correo': 'usuario@example.test',
        'expira_en': int(time.time()) + 600,
        'verificado': False,
        'intentos': 0,
    }
    state.update(overrides)
    return state


def test_expired_recovery_session_cannot_reach_password_update(client):
    with client.session_transaction() as session:
        session['estado_recuperacion_contrasena'] = _recovery_state(
            expira_en=int(time.time()) - 1,
            verificado=True,
            permiso_cambio='Abc1234567',
        )

    response = client.get('/actualizar-contrasena')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/recuperar-contrasena')
    with client.session_transaction() as session:
        assert 'estado_recuperacion_contrasena' not in session


def test_expired_database_code_cannot_be_consumed(monkeypatch):
    state = {'codigo': '123456', 'vigente': False}
    connection = RecoveryConnection(state)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: connection)

    valid = modelsRecuperacion.verificar_codigo_recuperacion(
        7,
        '123456',
        consumir=True,
        codigo_consumido='Abc1234567',
        expiracion_consumido='2026-08-29 12:00:00',
    )

    assert valid is False
    assert connection.rolled_back is True


def test_recovery_code_cannot_be_reused_after_consumption(monkeypatch):
    state = {'codigo': '123456', 'vigente': True}
    connections = []

    def connection_factory():
        connection = RecoveryConnection(state)
        connections.append(connection)
        return connection

    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', connection_factory)

    first_use = modelsRecuperacion.verificar_codigo_recuperacion(
        7,
        '123456',
        consumir=True,
        codigo_consumido='Abc1234567',
        expiracion_consumido='2026-08-29 12:00:00',
    )
    second_use = modelsRecuperacion.verificar_codigo_recuperacion(
        7,
        '123456',
        consumir=True,
        codigo_consumido='Xyz9876543',
        expiracion_consumido='2026-08-29 12:05:00',
    )

    assert first_use is True
    assert second_use is False
    assert state['codigo'] == 'Abc1234567'
    assert connections[0].committed is True
    assert connections[1].rolled_back is True


def test_fifth_invalid_code_clears_recovery_and_invalidates_database_code(
        client, monkeypatch):
    deleted_user_ids = []
    monkeypatch.setattr(
        autenticacion_bp,
        'verificar_codigo_recuperacion',
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        autenticacion_bp,
        'eliminar_codigos_recuperacion',
        lambda user_id: deleted_user_ids.append(user_id) or True,
    )
    with client.session_transaction() as session:
        session['estado_recuperacion_contrasena'] = _recovery_state()

    for _ in range(4):
        response = client.post('/verificar-codigo', data={'codigo': '000000'})
        assert response.status_code == 200

    response = client.post('/verificar-codigo', data={'codigo': '000000'})

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/recuperar-contrasena')
    assert deleted_user_ids == [7]
    with client.session_transaction() as session:
        assert 'estado_recuperacion_contrasena' not in session
