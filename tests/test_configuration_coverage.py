import pytest

import bd
from config import config_for_environment
from models import modelsLimpieza
from tests.db_fakes import FakeConnection


def _clear_database_environment(monkeypatch):
    for name in (
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_SSL_CA',
        'DB_HOST_LOCAL', 'DB_PORT_LOCAL', 'DB_USER_LOCAL', 'DB_PASS_LOCAL',
        'DB_NAME_LOCAL', 'DB_HOST_CLOUD', 'DB_PORT_CLOUD', 'DB_USER_CLOUD',
        'DB_PASS_CLOUD', 'DB_NAME_CLOUD',
    ):
        monkeypatch.delenv(name, raising=False)


def test_config_environment_variants_and_unknown(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'secret')
    monkeypatch.setenv('FLASK_DEBUG', 'true')
    assert config_for_environment('development')['DEBUG'] is True
    assert config_for_environment('testing')['TESTING'] is True
    assert config_for_environment('production')['SESSION_COOKIE_SECURE'] is True

    with pytest.raises(RuntimeError, match='APP_ENV no válido'):
        config_for_environment('unknown')
    with pytest.raises(RuntimeError, match='APP_ENV no válido'):
        config_for_environment(None)


def test_pool_rejects_incomplete_configuration(monkeypatch):
    _clear_database_environment(monkeypatch)
    monkeypatch.setenv('APP_ENV', 'LOCAL')
    monkeypatch.setattr(bd, '_pool', None)
    with pytest.raises(RuntimeError, match='incompleta'):
        bd._crear_pool()


def test_pool_uses_legacy_local_variables(monkeypatch):
    _clear_database_environment(monkeypatch)
    monkeypatch.setenv('APP_ENV', 'LOCAL')
    monkeypatch.setenv('DB_HOST_LOCAL', 'localhost')
    monkeypatch.setenv('DB_PORT_LOCAL', '3307')
    monkeypatch.setenv('DB_USER_LOCAL', 'user')
    monkeypatch.setenv('DB_PASS_LOCAL', 'password')
    monkeypatch.setenv('DB_NAME_LOCAL', 'database')
    captured = {}
    pool = object()
    monkeypatch.setattr(bd, 'PooledDB', lambda **kwargs: captured.update(kwargs) or pool)
    monkeypatch.setattr(bd, '_pool', None)

    bd._crear_pool()

    assert bd._pool is pool
    assert captured['port'] == 3307
    assert captured['mincached'] == 2
    assert 'ssl_ca' not in captured


def test_cloud_pool_requires_existing_ca_and_enables_tls(monkeypatch, tmp_path):
    _clear_database_environment(monkeypatch)
    monkeypatch.setenv('APP_ENV', 'NUBE')
    monkeypatch.setenv('DB_HOST_CLOUD', 'cloud.example.test')
    monkeypatch.setenv('DB_PORT_CLOUD', '3306')
    monkeypatch.setenv('DB_USER_CLOUD', 'user')
    monkeypatch.setenv('DB_PASS_CLOUD', 'password')
    monkeypatch.setenv('DB_NAME_CLOUD', 'database')
    monkeypatch.setattr(bd, '_pool', None)

    with pytest.raises(RuntimeError, match='DB_SSL_CA es obligatorio'):
        bd._crear_pool()

    monkeypatch.setenv('DB_SSL_CA', str(tmp_path / 'missing.pem'))
    with pytest.raises(RuntimeError, match='no apunta'):
        bd._crear_pool()

    ca_path = tmp_path / 'ca.pem'
    ca_path.write_text('certificate', encoding='utf-8')
    monkeypatch.setenv('DB_SSL_CA', str(ca_path))
    captured = {}
    pool = object()
    monkeypatch.setattr(bd, 'PooledDB', lambda **kwargs: captured.update(kwargs) or pool)
    bd._crear_pool()

    assert captured['mincached'] == 0
    assert captured['ssl_ca'] == str(ca_path)
    assert captured['ssl_verify_cert'] is True
    assert captured['ssl_verify_identity'] is True


def test_connection_reuses_existing_pool(monkeypatch):
    sentinel = object()

    class Pool:
        def connection(self):
            return sentinel

    monkeypatch.setattr(bd, '_pool', Pool())
    assert bd.Conexion_BD() is sentinel


@pytest.mark.parametrize(
    'function_name',
    ['limpiar_validaciones_expiradas', 'limpiar_codigos_recuperacion_expirados'],
)
def test_cleanup_success_and_database_error(monkeypatch, function_name):
    def handler(sql, params, cursor):
        cursor.rowcount = 3

    successful = FakeConnection(handler)
    monkeypatch.setattr(modelsLimpieza, 'Conexion_BD', lambda: successful)
    assert getattr(modelsLimpieza, function_name)() == 3
    assert successful.commits == 1
    assert successful.closed is True

    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    failed = FakeConnection(fail)
    monkeypatch.setattr(modelsLimpieza, 'Conexion_BD', lambda: failed)
    assert getattr(modelsLimpieza, function_name)() == 0
    assert failed.rollbacks == 1
    assert failed.closed is True
