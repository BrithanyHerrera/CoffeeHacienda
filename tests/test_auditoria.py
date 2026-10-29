import json

from models.modelsAuditoria import registrar_evento
from tests.db_fakes import FakeConnection


def test_registrar_evento_serializa_detalles_y_limita_metadatos():
    connection = FakeConnection(lambda sql, params, cursor: None)
    registrar_evento(
        connection.cursor_instance,
        'ACTUALIZAR',
        'producto',
        entidad_id=12,
        usuario_id=3,
        detalles={'nombre': 'Café ☕', 'fecha': '2026-09-01'},
    )

    sql, params = connection.cursor_instance.calls[0]
    assert sql.startswith('INSERT INTO tauditoria')
    assert params[:4] == (3, 'ACTUALIZAR', 'producto', 12)
    assert json.loads(params[4])['nombre'] == 'Café ☕'


def test_registrar_evento_acepta_detalles_vacios():
    connection = FakeConnection(lambda sql, params, cursor: None)
    registrar_evento(connection.cursor_instance, 'BAJA', 'usuario')

    assert connection.cursor_instance.calls[0][1] == (None, 'BAJA', 'usuario', None, None)


def test_registrar_evento_tolera_migracion_pendiente():
    class MissingAuditTable(Exception):
        args = (1146, 'table does not exist')

    class MissingCursor:
        def execute(self, sql, params):
            raise MissingAuditTable()

    assert registrar_evento(MissingCursor(), 'CREAR', 'venta') is False


def test_registrar_evento_propaga_errores_distintos():
    class DatabaseError(Exception):
        args = (1064, 'syntax error')

    class ErrorCursor:
        def execute(self, sql, params):
            raise DatabaseError()

    try:
        registrar_evento(ErrorCursor(), 'CREAR', 'venta')
    except DatabaseError:
        pass
    else:
        raise AssertionError('El error de base de datos debe propagarse')


def test_auditoria_ajustar_stock_registra_motivo(monkeypatch):
    from models import modelsInventario

    def handler(sql, params, cursor):
        cursor.rowcount = 1
        if sql.startswith('SELECT stock'):
            return {'stock': 10}
        return None

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsInventario, 'Conexion_BD', lambda: connection)

    modelsInventario.actualizar_stock_producto(
        5, 15, 2, 20, motivo='Reabastecimiento con proveedor'
    )

    auditoria_calls = [
        (sql, params) for sql, params in connection.cursor_instance.calls
        if sql.startswith('INSERT INTO tauditoria')
    ]
    assert len(auditoria_calls) == 1
    sql, params = auditoria_calls[0]
    assert params[1] == 'AJUSTAR_STOCK'
    assert params[2] == 'producto'
    assert params[3] == 5
    detalles = json.loads(params[4])
    assert detalles['motivo'] == 'Reabastecimiento con proveedor'
    assert detalles['stock_anterior'] == 10
    assert detalles['stock_nuevo'] == 15
    assert detalles['cantidad'] == 5

