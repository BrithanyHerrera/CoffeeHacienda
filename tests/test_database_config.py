import bd


def test_testing_environment_uses_unified_database_variables(monkeypatch):
    captured = {}
    sentinel_pool = object()

    monkeypatch.setenv('APP_ENV', 'TESTING')
    monkeypatch.setenv('DB_HOST', 'mysql-ci')
    monkeypatch.setenv('DB_PORT', '3306')
    monkeypatch.setenv('DB_USER', 'ci-user')
    monkeypatch.setenv('DB_PASSWORD', 'ci-password')
    monkeypatch.setenv('DB_NAME', 'ci-database')
    monkeypatch.delenv('DB_HOST_LOCAL', raising=False)
    monkeypatch.delenv('DB_USER_LOCAL', raising=False)
    monkeypatch.delenv('DB_PASS_LOCAL', raising=False)
    monkeypatch.delenv('DB_NAME_LOCAL', raising=False)

    def fake_pool(**kwargs):
        captured.update(kwargs)
        return sentinel_pool

    monkeypatch.setattr(bd, 'PooledDB', fake_pool)
    monkeypatch.setattr(bd, '_pool', None)

    bd._crear_pool()

    assert bd._pool is sentinel_pool
    assert captured['host'] == 'mysql-ci'
    assert captured['port'] == 3306
    assert captured['user'] == 'ci-user'
    assert captured['password'] == 'ci-password'
    assert captured['database'] == 'ci-database'
    assert 'ssl_ca' not in captured
