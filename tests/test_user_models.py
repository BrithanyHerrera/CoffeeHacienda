from datetime import datetime, timedelta

import pytest

from models import modelsUsuarios
from tests.db_fakes import FakeConnection, connection_with_results


def _failing_connection():
    def fail(sql, params, cursor):
        raise RuntimeError('database error')

    return FakeConnection(fail)


def test_update_user_rejects_duplicate_username_and_email(monkeypatch):
    duplicate_name = connection_with_results({'count': 1})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: duplicate_name)
    assert modelsUsuarios.actualizar_usuario(
        1, 'duplicado', None, 'nuevo@example.test', 1
    ) == (False, 'El nombre de usuario ya está en uso por otro usuario')

    duplicate_email = connection_with_results({'count': 0}, {'count': 1})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: duplicate_email)
    assert modelsUsuarios.actualizar_usuario(
        1, 'nuevo', None, 'duplicado@example.test', 1
    ) == (False, 'El correo electrónico ya está registrado por otro usuario')


@pytest.mark.parametrize('password', ['hash-nuevo', None])
def test_update_user_with_and_without_password(monkeypatch, password):
    connection = connection_with_results({'count': 0}, {'count': 0}, None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)

    assert modelsUsuarios.actualizar_usuario(
        1, 'usuario', password, 'correo@example.test', 2
    ) == (True, 'Usuario actualizado exitosamente')
    update_sql = connection.cursor_instance.calls[2][0]
    assert ('sesion_version=sesion_version + 1' in update_sql) is bool(password)


def test_update_user_handles_database_error(monkeypatch):
    connection = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)
    assert modelsUsuarios.actualizar_usuario(
        1, 'usuario', None, 'correo@example.test', 2
    ) == (False, 'No fue posible actualizar el usuario')
    assert connection.rollbacks == 1


@pytest.mark.parametrize(
    ('function_name', 'args', 'result'),
    [
        ('obtener_usuario_por_id', (1,), {'Id': 1}),
        ('obtener_roles', (), [{'Id': 1, 'rol': 'Administrador'}]),
        ('obtener_usuario_por_correo', ('correo@example.test',), {'Id': 1}),
        ('obtener_usuarios_activos', (), [{'Id': 1}]),
        ('obtener_usuarios_inactivos', (), [{'Id': 2}]),
    ],
)
def test_user_read_functions_return_data(
        monkeypatch, function_name, args, result):
    connection = connection_with_results(result)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)
    assert getattr(modelsUsuarios, function_name)(*args) == result
    assert connection.closed is True


@pytest.mark.parametrize(
    ('function_name', 'args', 'expected'),
    [
        ('obtener_usuario_por_id', (1,), None),
        ('obtener_roles', (), []),
        ('obtener_usuario_por_correo', ('correo@example.test',), None),
        ('obtener_usuarios_activos', (), []),
        ('obtener_usuarios_inactivos', (), []),
    ],
)
def test_user_read_functions_handle_errors(
        monkeypatch, function_name, args, expected):
    connection = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)
    assert getattr(modelsUsuarios, function_name)(*args) == expected


def test_save_pending_user_rejects_existing_and_pending_email(monkeypatch):
    existing = connection_with_results({'Id': 1})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: existing)
    assert modelsUsuarios.guardar_usuario_pendiente(
        'usuario', 'hash', 'correo@example.test', 2
    ) == (False, 'Ya existe un usuario con ese correo electrónico', None)

    pending = connection_with_results(None, {'id': 3})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: pending)
    assert modelsUsuarios.guardar_usuario_pendiente(
        'usuario', 'hash', 'correo@example.test', 2
    ) == (False, 'Ya existe una solicitud pendiente para este correo', None)


def test_save_pending_user_success_and_error(monkeypatch):
    monkeypatch.setattr(modelsUsuarios, 'generar_codigo', lambda: '123456')

    def handler(sql, params, cursor):
        if sql.startswith('INSERT INTO tvalidacion_usuarios'):
            cursor.lastrowid = 9
        return None

    successful = FakeConnection(handler)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: successful)
    assert modelsUsuarios.guardar_usuario_pendiente(
        'usuario', 'hash', 'correo@example.test', 2
    ) == (
        True,
        'Usuario pendiente de validación',
        {'id': 9, 'codigo': '123456'},
    )

    failed = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: failed)
    assert modelsUsuarios.guardar_usuario_pendiente(
        'usuario', 'hash', 'correo@example.test', 2
    ) == (False, 'No fue posible guardar el usuario pendiente', None)


def _validation(**overrides):
    result = {
        'id': 5,
        'usuario': 'nuevo',
        'contrasena': 'hash',
        'correo': 'correo@example.test',
        'rol_id': 2,
        'fecha_creacion': datetime.now(),
    }
    result.update(overrides)
    return result


def test_validate_user_code_missing_and_expired(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: missing)
    assert modelsUsuarios.validar_codigo_usuario('correo@example.test', '000000') == (
        False,
        'Código de validación incorrecto o expirado',
    )

    expired = connection_with_results(
        _validation(fecha_creacion=datetime.now() - timedelta(minutes=31))
    )
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: expired)
    assert modelsUsuarios.validar_codigo_usuario('correo@example.test', '000000') == (
        False,
        'El código de validación ha expirado',
    )


@pytest.mark.parametrize(
    ('validation', 'expected_message', 'expected_sql'),
    [
        (_validation(), 'Usuario validado correctamente', 'INSERT INTO tusuarios'),
        (
            _validation(usuario='__CAMBIO_CORREO__7'),
            'Correo electrónico actualizado y validado correctamente',
            'UPDATE tusuarios SET correo',
        ),
    ],
)
def test_validate_user_code_creates_user_or_changes_email(
        monkeypatch, validation, expected_message, expected_sql):
    connection = connection_with_results(validation, None, None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)

    assert modelsUsuarios.validar_codigo_usuario(
        validation['correo'], '123456'
    ) == (True, expected_message)
    assert expected_sql in connection.cursor_instance.calls[1][0]
    assert connection.commits == 1


def test_validate_user_code_handles_database_error(monkeypatch):
    connection = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)
    assert modelsUsuarios.validar_codigo_usuario('correo@example.test', '123456') == (
        False,
        'No fue posible validar el código',
    )


def test_resend_validation_code_missing_success_and_error(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: missing)
    assert modelsUsuarios.reenviar_codigo_validacion('correo@example.test') == (
        False,
        'No se encontró una solicitud pendiente para este correo',
        None,
    )

    monkeypatch.setattr(modelsUsuarios, 'generar_codigo', lambda: '654321')
    successful = connection_with_results({'id': 8}, None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: successful)
    assert modelsUsuarios.reenviar_codigo_validacion('correo@example.test') == (
        True,
        'Código regenerado correctamente',
        '654321',
    )

    failed = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: failed)
    assert modelsUsuarios.reenviar_codigo_validacion('correo@example.test') == (
        False,
        'No fue posible reenviar el código',
        None,
    )


def test_reactivate_user_success_and_error(monkeypatch):
    successful = connection_with_results(None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: successful)
    assert modelsUsuarios.reactivar_usuario(1) is True

    failed = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: failed)
    assert modelsUsuarios.reactivar_usuario(1) is False
    assert failed.rollbacks == 1


def test_deactivate_user_missing_success_and_error(monkeypatch):
    missing = connection_with_results(None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: missing)
    assert modelsUsuarios.desactivar_usuario(1) == (False, 'Usuario no encontrado')

    successful = connection_with_results({'Id': 1}, None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: successful)
    assert modelsUsuarios.desactivar_usuario(1) == (
        True,
        'Usuario desactivado exitosamente',
    )

    failed = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: failed)
    assert modelsUsuarios.desactivar_usuario(1) == (
        False,
        'No fue posible desactivar el usuario',
    )


def test_email_exists_and_pending_validation_lookup(monkeypatch):
    exists = connection_with_results({'Id': 1})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: exists)
    assert modelsUsuarios.correo_existe_en_usuarios('correo@example.test') is True

    absent = connection_with_results(None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: absent)
    assert modelsUsuarios.correo_existe_en_usuarios('correo@example.test') is False

    pending = {'id': 4, 'correo': 'correo@example.test'}
    connection = connection_with_results(pending)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: connection)
    assert modelsUsuarios.obtener_validacion_pendiente(4) == pending


def test_update_pending_email_conflict_success_no_change_and_error(monkeypatch):
    conflict = connection_with_results({'id': 2})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: conflict)
    assert modelsUsuarios.actualizar_correo_validacion(
        1, 'viejo@example.test', 'nuevo@example.test', '123456'
    ) is False

    def success_handler(sql, params, cursor):
        if sql.startswith('UPDATE tvalidacion_usuarios'):
            cursor.rowcount = 1

    successful = FakeConnection(success_handler)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: successful)
    assert modelsUsuarios.actualizar_correo_validacion(
        1, 'viejo@example.test', 'nuevo@example.test', '123456'
    ) is True

    unchanged = connection_with_results(None, None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: unchanged)
    assert modelsUsuarios.actualizar_correo_validacion(
        1, 'viejo@example.test', 'nuevo@example.test', '123456'
    ) is False

    failed = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: failed)
    assert modelsUsuarios.actualizar_correo_validacion(
        1, 'viejo@example.test', 'nuevo@example.test', '123456'
    ) is False


def test_save_pending_email_change_rejects_conflicts_and_missing_user(monkeypatch):
    existing = connection_with_results({'Id': 2})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: existing)
    assert modelsUsuarios.guardar_cambio_correo_pendiente(
        1, 'nuevo@example.test', '123456'
    ) is None

    pending = connection_with_results(None, {'id': 3})
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: pending)
    assert modelsUsuarios.guardar_cambio_correo_pendiente(
        1, 'nuevo@example.test', '123456'
    ) is None

    missing_user = connection_with_results(None, None, None)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: missing_user)
    assert modelsUsuarios.guardar_cambio_correo_pendiente(
        1, 'nuevo@example.test', '123456'
    ) is None


def test_save_pending_email_change_success_and_error(monkeypatch):
    def handler(sql, params, cursor):
        if sql.startswith('SELECT Id FROM tusuarios'):
            return None
        if sql.startswith('SELECT id FROM tvalidacion_usuarios'):
            return None
        if sql.startswith('SELECT rol_id'):
            return {'rol_id': 2}
        if sql.startswith('INSERT INTO tvalidacion_usuarios'):
            cursor.lastrowid = 12
        return None

    successful = FakeConnection(handler)
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: successful)
    assert modelsUsuarios.guardar_cambio_correo_pendiente(
        1, 'nuevo@example.test', '123456'
    ) == 12

    failed = _failing_connection()
    monkeypatch.setattr(modelsUsuarios, 'Conexion_BD', lambda: failed)
    assert modelsUsuarios.guardar_cambio_correo_pendiente(
        1, 'nuevo@example.test', '123456'
    ) is None
