from decimal import Decimal

import pytest

from models import modelsVentas
from models import modelsCorteCaja


class FakeCursor:
    def __init__(self, handler):
        self.handler = handler
        self.result = None
        self.rowcount = 0
        self.lastrowid = None
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, params=None):
        normalized = ' '.join(sql.split())
        self.calls.append((normalized, params))
        response = self.handler(normalized, params, self)
        self.result = response
        return 1

    def fetchone(self):
        if isinstance(self.result, list):
            return self.result[0] if self.result else None
        return self.result

    def fetchall(self):
        if self.result is None:
            return []
        return self.result if isinstance(self.result, list) else [self.result]


class FakeConnection:
    def __init__(self, handler):
        self.cursor_instance = FakeCursor(handler)
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


def test_sale_uses_official_price_and_records_stock_movement(monkeypatch):
    captured = {}

    def handler(sql, params, cursor):
        if 'FROM tmetodospago' in sql:
            return {'Id': 1, 'codigo': 'EFECTIVO', 'tipo_de_pago': 'Efectivo'}
        if 'FROM tproductos p JOIN tcategorias' in sql:
            return [{
                'id': 10,
                'nombre_producto': 'Producto oficial',
                'precio': Decimal('25.00'),
                'stock': 10,
                'requiere_inventario': 1,
            }]
        if 'FROM tproductos_variantes pv' in sql:
            return []
        if 'SELECT Id FROM tclientes' in sql:
            return None
        if sql.startswith('INSERT INTO tclientes'):
            cursor.lastrowid = 20
            return None
        if 'SELECT Id FROM tusuarios' in sql:
            return {'Id': 5}
        if 'SELECT Id FROM testadosventa' in sql:
            return {'Id': 1}
        if sql.startswith('INSERT INTO tventas'):
            captured['sale_params'] = params
            cursor.lastrowid = 99
            return None
        if 'FROM information_schema.COLUMNS' in sql:
            return {'total': 1}
        if sql.startswith('INSERT INTO tdetalleventas'):
            captured['detail_params'] = params
            return None
        if sql.startswith('UPDATE tproductos SET stock = stock -'):
            cursor.rowcount = 1
            return None
        if sql.startswith('INSERT INTO tmovimientosinventario'):
            captured['movement_params'] = params
            return None
        raise AssertionError(f'Consulta inesperada: {sql}')

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)

    success, _, data = modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 10, 'cantidad': 2}],
        total='0.01', metodo_pago_id=1, usuario_actual='vendedor',
        dinero_recibido='100.00', cambio='999.00',
    )

    assert success is True
    assert data['total'] == '50.00'
    assert data['cambio'] == '50.00'
    assert captured['sale_params'][2] == Decimal('50.00')
    assert captured['detail_params'][3:5] == ('Producto oficial', 'No aplica')
    assert captured['movement_params'] == (10, 99, 5, 2, 'Salida por venta')
    assert connection.committed is True


@pytest.mark.parametrize('quantity', [0, -1, 1.5, True, '2.5'])
def test_sale_rejects_invalid_quantities(monkeypatch, quantity):
    def handler(sql, params, cursor):
        if 'FROM tmetodospago' in sql:
            return {'Id': 1, 'codigo': 'EFECTIVO', 'tipo_de_pago': 'Efectivo'}
        raise AssertionError(f'No debía continuar: {sql}')

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)

    success, _, _ = modelsVentas.procesar_venta_completa(
        'Cliente', '1', [{'id': 10, 'cantidad': quantity}],
        total=1, metodo_pago_id=1, usuario_actual='vendedor',
    )

    assert success is False
    assert connection.committed is False


def test_cancel_restores_stock_once_and_records_audit(monkeypatch):
    captured = {'movements': 0}

    def handler(sql, params, cursor):
        if sql.startswith('SELECT estado_id FROM tventas'):
            return {'estado_id': 1}
        if 'SUM(dv.cantidad)' in sql:
            return [{'producto_id': 10, 'cantidad': 2}]
        if sql.startswith('UPDATE tproductos SET stock = stock +'):
            cursor.rowcount = 1
            return None
        if sql.startswith('INSERT INTO tmovimientosinventario'):
            captured['movements'] += 1
            captured['movement_params'] = params
            return None
        if sql.startswith('UPDATE tventas SET estado_id = 3'):
            cursor.rowcount = 1
            captured['cancel_params'] = params
            return None
        raise AssertionError(f'Consulta inesperada: {sql}')

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsVentas, 'Conexion_BD', lambda: connection)

    assert modelsVentas.cancelar_orden(50, 7, 'Pedido duplicado') is True
    assert captured['movements'] == 1
    assert captured['movement_params'] == (
        10, 50, 7, 2, 'Cancelación de venta: Pedido duplicado'
    )
    assert captured['cancel_params'] == (7, 'Pedido duplicado', 50, 1)
    assert connection.committed is True


def test_cash_register_groups_payments_by_stable_code(monkeypatch):
    def handler(sql, params, cursor):
        assert 'JOIN tmetodospago' in sql
        assert 'GROUP BY mp.codigo' in sql
        return [
            {'codigo': 'TRANSFERENCIA', 'total': Decimal('40.00')},
            {'codigo': 'EFECTIVO', 'total': Decimal('25.00')},
            {'codigo': 'TARJETA', 'total': Decimal('10.00')},
        ]

    connection = FakeConnection(handler)
    monkeypatch.setattr(modelsCorteCaja, 'Conexion_BD', lambda: connection)

    totals = modelsCorteCaja.filtrar_ventas(
        '2026-08-28 00:00:00', '2026-08-28 23:59:59'
    )

    assert totals == {
        'efectivo': Decimal('25.00'),
        'tarjeta': Decimal('10.00'),
        'transferencias': Decimal('40.00'),
    }
