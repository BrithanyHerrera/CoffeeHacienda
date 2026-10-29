from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from models import modelsCorteCaja, modelsRecuperacion
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_corte_caja_agrupa_pagos_por_metodo(monkeypatch):
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


def test_funciones_lectura_corte_caja(monkeypatch):
    cuts = [{'Id': 1}]
    all_cuts = connection_with_results(cuts)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: all_cuts)
    assert modelsCorteCaja.obtener_todos_cortes() == cuts

    reports = connection_with_results(cuts)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: reports)
    assert modelsCorteCaja.obtener_cortes_con_ganancia() == cuts

    # Ultimo corte y fecha sugerida
    last_cut = {'Id': 2, 'fecha_hora_cierre': datetime(2026, 10, 27, 18, 0)}
    last_cut_conn = connection_with_results(last_cut)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: last_cut_conn)
    assert modelsCorteCaja.obtener_ultimo_corte() == last_cut

    monkeypatch.setattr(modelsCorteCaja, 'obtener_ultimo_corte', lambda: last_cut)
    fecha, tiene_previo = modelsCorteCaja.obtener_fecha_sugerida_inicio()
    assert tiene_previo is True
    assert fecha == last_cut['fecha_hora_cierre']

    # Sin corte previo, busca primera venta
    monkeypatch.setattr(modelsCorteCaja, 'obtener_ultimo_corte', lambda: None)
    venta_row = {'primera_fecha': datetime(2026, 10, 1, 8, 0)}
    venta_conn = connection_with_results(venta_row)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: venta_conn)
    fecha, tiene_previo = modelsCorteCaja.obtener_fecha_sugerida_inicio()
    assert tiene_previo is False
    assert fecha == venta_row['primera_fecha']

    # Manejo de error al obtener ultimo corte
    failed = _failing_connection()
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: failed)
    assert modelsCorteCaja.obtener_ultimo_corte() is None


def test_guardar_corte_caja_rechaza_traslape_y_maneja_error(monkeypatch):
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


def test_obtener_corte_caja_por_id_exito_y_error(monkeypatch):
    cut = {'id': 1}
    successful = connection_with_results(cut)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: successful)
    assert modelsCorteCaja.obtener_corte_por_id(1) == cut

    failed = _failing_connection()
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: failed)
    assert modelsCorteCaja.obtener_corte_por_id(1) is None


@pytest.mark.parametrize('length', [3, 11, '6'])
def test_codigo_recuperacion_rechaza_longitudes_invalidas(length):
    with pytest.raises(ValueError):
        modelsRecuperacion.generar_codigo(length)


def test_codigo_recuperacion_es_numerico(monkeypatch):
    monkeypatch.setattr(modelsRecuperacion.secrets, 'choice', lambda values: values[-1])
    assert modelsRecuperacion.generar_codigo(4) == '9999'


def test_guardar_codigo_recuperacion_exito_y_error(monkeypatch):
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
def test_verificar_codigo_recuperacion_rechaza_formato_invalido(code):
    assert modelsRecuperacion.verificar_codigo_recuperacion(1, code) is False


def test_verificar_codigo_recuperacion_faltante_discordancia_y_sin_consumir(monkeypatch):
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
def test_consumir_codigo_recuperacion_requiere_reemplazo_valido(
        monkeypatch, replacement, expiration):
    connection = connection_with_results({'Id': 1, 'codigo': '123456'})
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: connection)
    assert modelsRecuperacion.verificar_codigo_recuperacion(
        1, '123456', True, replacement, expiration
    ) is False


def test_consumir_codigo_recuperacion_fallo_exito_y_excepcion(monkeypatch):
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


def test_eliminar_codigos_recuperacion_exito_y_error(monkeypatch):
    successful = connection_with_results(None)
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: successful)
    assert modelsRecuperacion.eliminar_codigos_recuperacion(1) is True

    failed = _failing_connection()
    monkeypatch.setattr(modelsRecuperacion, 'Conexion_BD', lambda: failed)
    assert modelsRecuperacion.eliminar_codigos_recuperacion(1) is False


@pytest.mark.parametrize('permission', ['', None, '12345678901'])
def test_actualizar_contrasena_rechaza_permiso_invalido(permission):
    assert modelsRecuperacion.actualizar_contrasena_por_codigo(
        1, 'hash', permission
    ) is False


def test_actualizar_contrasena_rechaza_faltante_discordancia_y_fallo(monkeypatch):
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


def test_actualizar_contrasena_requiere_eliminar_luego_commit_y_error(monkeypatch):
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
