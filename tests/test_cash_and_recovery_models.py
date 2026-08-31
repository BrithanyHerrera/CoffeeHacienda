from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from models import modelsCorteCaja, modelsRecuperacion
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_cash_totals_empty_all_payment_codes_and_error(monkeypatch):
    assert modelsCorteCaja.filtrar_ventas(None, None) == {
        'efectivo': Decimal('0.00'),
        'tarjeta': Decimal('0.00'),
        'transferencias': Decimal('0.00'),
    }

    rows = [
        {'codigo': 'EFECTIVO', 'total': Decimal('10.00')},
        {'codigo': 'TARJETA', 'total': Decimal('20.00')},
        {'codigo': 'TRANSFERENCIA', 'total': Decimal('30.00')},
        {'codigo': 'OTRO', 'total': Decimal('99.00')},
    ]
    connection = connection_with_results(rows)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: connection)
    assert modelsCorteCaja.filtrar_ventas('inicio', 'fin') == {
        'efectivo': Decimal('10.00'),
        'tarjeta': Decimal('20.00'),
        'transferencias': Decimal('30.00'),
    }

    monkeypatch.setattr(
        modelsCorteCaja,
        'Conexion_BD',
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert modelsCorteCaja.filtrar_ventas('inicio', 'fin') == {
        'efectivo': Decimal('0.00'),
        'tarjeta': Decimal('0.00'),
        'transferencias': Decimal('0.00'),
    }


def test_cash_cut_read_functions(monkeypatch):
    cuts = [{'Id': 1}]
    all_cuts = connection_with_results(cuts)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: all_cuts)
    assert modelsCorteCaja.obtener_todos_cortes() == cuts

    reports = connection_with_results(cuts)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: reports)
    assert modelsCorteCaja.obtener_cortes_con_ganancia() == cuts


def test_save_cash_cut_rejects_overlap_succeeds_and_handles_error(monkeypatch):
    overlap = connection_with_results({'Id': 1})
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: overlap)
    assert modelsCorteCaja.guardar_corte_caja(
        1, 'inicio', 'fin', 100, 100, 0, 0, 100, 0, 0
    ) == (False, 'Ya existe un corte que se cruza con ese periodo', None)
    assert overlap.rollbacks == 1

    def handler(sql, params, cursor):
        if sql.startswith('INSERT INTO tcortescaja'):
            cursor.lastrowid = 7
        return None

    successful = FakeConnection(handler)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: successful)
    assert modelsCorteCaja.guardar_corte_caja(
        1, 'inicio', 'fin', 100, 60, 20, 20, 100, 10, 5
    ) == (True, 'Corte registrado correctamente', 7)

    failed = _failing_connection()
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: failed)
    assert modelsCorteCaja.guardar_corte_caja(
        1, 'inicio', 'fin', 100, 100, 0, 0, 100, 0, 0
    ) == (False, 'No se pudo registrar el corte', None)


def test_get_cash_cut_by_id_success_and_error(monkeypatch):
    cut = {'id': 1}
    successful = connection_with_results(cut)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: successful)
    assert modelsCorteCaja.obtener_corte_por_id(1) == cut

    failed = _failing_connection()
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: failed)
    assert modelsCorteCaja.obtener_corte_por_id(1) is None


@pytest.mark.parametrize('length', [3, 11, '6'])
def test_recovery_code_rejects_invalid_lengths(length):
    with pytest.raises(ValueError):
        modelsRecuperacion.generar_codigo(length)


def test_recovery_code_is_numeric(monkeypatch):
    monkeypatch.setattr(modelsRecuperacion.secrets, 'choice', lambda values: values[-1])
    assert modelsRecuperacion.generar_codigo(4) == '9999'


def test_save_recovery_code_success_and_error(monkeypatch):
    successful = connection_with_results(None, None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: successful)
    assert modelsRecuperacion.guardar_codigo_recuperacion(
        1, '123456', datetime.now() + timedelta(minutes=30)
    ) is True

    failed = _failing_connection()
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: failed)
    assert modelsRecuperacion.guardar_codigo_recuperacion(
        1, '123456', datetime.now()
    ) is False
    assert failed.rollbacks == 1


@pytest.mark.parametrize('code', ['', None, '12345678901', 'abcdef'])
def test_verify_recovery_code_rejects_invalid_format(code):
    assert modelsRecuperacion.verificar_codigo_recuperacion(1, code) is False


def test_verify_recovery_code_missing_mismatch_and_without_consuming(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: missing)
    assert modelsRecuperacion.verificar_codigo_recuperacion(1, '123456') is False

    mismatch = connection_with_results({'Id': 1, 'codigo': '654321'})
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: mismatch)
    assert modelsRecuperacion.verificar_codigo_recuperacion(1, '123456') is False

    valid = connection_with_results({'Id': 1, 'codigo': '123456'})
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: valid)
    assert modelsRecuperacion.verificar_codigo_recuperacion(1, '123456') is True
    assert valid.rollbacks == 1


@pytest.mark.parametrize(
    ('replacement', 'expiration'),
    [('', datetime.now()), ('12345678901', datetime.now()), ('nuevo', None)],
)
def test_consume_recovery_code_requires_valid_replacement(
        monkeypatch, replacement, expiration):
    connection = connection_with_results({'Id': 1, 'codigo': '123456'})
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: connection)
    assert modelsRecuperacion.verificar_codigo_recuperacion(
        1, '123456', True, replacement, expiration
    ) is False


def test_consume_recovery_code_update_failure_success_and_exception(monkeypatch):
    no_update = connection_with_results({'Id': 1, 'codigo': '123456'}, None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: no_update)
    assert modelsRecuperacion.verificar_codigo_recuperacion(
        1, '123456', True, 'permiso123', datetime.now()
    ) is False

    def handler(sql, params, cursor):
        if sql.startswith('SELECT Id, codigo'):
            return {'Id': 1, 'codigo': '123456'}
        cursor.rowcount = 1

    successful = FakeConnection(handler)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: successful)
    assert modelsRecuperacion.verificar_codigo_recuperacion(
        1, '123456', True, 'permiso123', datetime.now()
    ) is True
    assert successful.commits == 1

    failed = _failing_connection()
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: failed)
    assert modelsRecuperacion.verificar_codigo_recuperacion(1, '123456') is False


def test_delete_recovery_codes_success_and_error(monkeypatch):
    successful = connection_with_results(None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: successful)
    assert modelsRecuperacion.eliminar_codigos_recuperacion(1) is True

    failed = _failing_connection()
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: failed)
    assert modelsRecuperacion.eliminar_codigos_recuperacion(1) is False


@pytest.mark.parametrize('permission', ['', None, '12345678901'])
def test_password_update_rejects_invalid_permission(permission):
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', permission
    ) is False


def test_password_update_rejects_missing_mismatch_and_user_update_failure(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: missing)
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', 'permiso123'
    ) is False

    mismatch = connection_with_results({'Id': 1, 'codigo': 'otro'})
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: mismatch)
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', 'permiso123'
    ) is False

    no_user = connection_with_results({'Id': 1, 'codigo': 'permiso123'}, None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: no_user)
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', 'permiso123'
    ) is False


def test_password_update_requires_delete_then_commits_and_handles_error(monkeypatch):
    calls = {'updates': 0}

    def no_delete_handler(sql, params, cursor):
        if sql.startswith('SELECT Id, codigo'):
            return {'Id': 1, 'codigo': 'permiso123'}
        calls['updates'] += 1
        cursor.rowcount = 1 if calls['updates'] == 1 else 0

    no_delete = FakeConnection(no_delete_handler)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: no_delete)
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', 'permiso123'
    ) is False

    def success_handler(sql, params, cursor):
        if sql.startswith('SELECT Id, codigo'):
            return {'Id': 1, 'codigo': 'permiso123'}
        cursor.rowcount = 1

    successful = FakeConnection(success_handler)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: successful)
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', 'permiso123'
    ) is True
    assert successful.commits == 1

    failed = _failing_connection()
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: failed)
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', 'permiso123'
    ) is False
