import os
import secrets
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from bd import Conexion_BD
from models.modelsCorteCaja import filtrar_ventas, guardar_corte_caja
from models.modelsVentas import (
    actualizar_estado_orden,
    cancelar_orden,
    obtener_venta_completa,
    procesar_venta_completa,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv('RUN_DB_WRITE_TESTS') != '1',
        reason='RUN_DB_WRITE_TESTS=1 habilita pruebas en una base aislada',
    ),
]


def _assert_isolated_database(cursor):
    cursor.execute('SELECT DATABASE() AS nombre')
    database_name = cursor.fetchone()['nombre']
    assert database_name.lower().endswith('_test'), (
        'Las pruebas de escritura exigen una base cuyo nombre termine en _test'
    )


@pytest.fixture
def pos_catalog():
    connection = Conexion_BD()
    marker = f'codex_{secrets.token_hex(6)}'
    try:
        with connection.cursor() as cursor:
            _assert_isolated_database(cursor)
            cursor.execute(
                'INSERT INTO tusuarios (usuario, contrasena, correo, rol_id) '
                'VALUES (%s, %s, %s, 1)',
                (marker, 'hash-no-utilizado', f'{marker}@example.test'),
            )
            user_id = cursor.lastrowid
            cursor.execute(
                'INSERT INTO tcategorias (categoria, requiere_inventario) VALUES (%s, 1)',
                (marker,),
            )
            category_id = cursor.lastrowid
            cursor.execute('INSERT INTO ttamanos (tamano) VALUES (%s)', (marker,))
            size_id = cursor.lastrowid
            cursor.execute(
                '''
                INSERT INTO tproductos
                    (nombre_producto, descripcion, precio, stock, stock_minimo,
                     stock_maximo, categoria_id, activo)
                VALUES (%s, 'Producto de integración', 50.00, 10, 1, 20, %s, 1)
                ''',
                ('Café de integración', category_id),
            )
            product_id = cursor.lastrowid
            cursor.execute(
                'INSERT INTO tproductos_variantes '
                '(producto_id, tamano_id, precio) VALUES (%s, %s, 60.00)',
                (product_id, size_id),
            )
            variant_id = cursor.lastrowid
        connection.commit()
        yield {
            'marker': marker,
            'user_id': user_id,
            'product_id': product_id,
            'variant_id': variant_id,
            'size_id': size_id,
            'category_id': category_id,
        }
    finally:
        connection.close()


def _stock_and_movements(product_id, sale_id):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT stock FROM tproductos WHERE Id = %s', (product_id,))
            stock = cursor.fetchone()['stock']
            cursor.execute(
                '''
                SELECT tipo_movimiento_id, cantidad
                FROM tmovimientosinventario
                WHERE venta_id = %s
                ORDER BY Id
                ''',
                (sale_id,),
            )
            movements = cursor.fetchall()
        return stock, movements
    finally:
        connection.close()


def test_catalog_sale_inventory_cancellation_and_cash_cut_flow(pos_catalog):
    started_at = datetime.now() - timedelta(minutes=1)
    success, _, sale = procesar_venta_completa(
        'Cliente integración',
        '7',
        [{
            'id': pos_catalog['product_id'],
            'variante_id': pos_catalog['variant_id'],
            'cantidad': 2,
        }],
        total='0.01',
        metodo_pago_id=1,
        usuario_actual=pos_catalog['marker'],
        dinero_recibido='150.00',
        cambio='999.00',
    )

    assert success is True
    assert sale['total'] == '120.00'
    assert sale['cambio'] == '30.00'
    stock_after_sale, movements_after_sale = _stock_and_movements(
        pos_catalog['product_id'], sale['venta_id']
    )
    assert stock_after_sale == 8
    assert movements_after_sale == [{'tipo_movimiento_id': 2, 'cantidad': 2}]

    assert cancelar_orden(
        sale['venta_id'], pos_catalog['user_id'], 'Cancelación de integración'
    ) is True
    assert cancelar_orden(
        sale['venta_id'], pos_catalog['user_id'], 'Reintento de integración'
    ) is True

    stock_after_cancel, movements_after_cancel = _stock_and_movements(
        pos_catalog['product_id'], sale['venta_id']
    )
    assert stock_after_cancel == 10
    assert movements_after_cancel == [
        {'tipo_movimiento_id': 2, 'cantidad': 2},
        {'tipo_movimiento_id': 1, 'cantidad': 2},
    ]

    ended_at = datetime.now() + timedelta(minutes=1)
    totals = filtrar_ventas(started_at, ended_at)
    assert totals == {
        'efectivo': Decimal('0.00'),
        'tarjeta': Decimal('0.00'),
        'transferencias': Decimal('0.00'),
    }
    saved, _, cut_id = guardar_corte_caja(
        pos_catalog['user_id'],
        started_at,
        ended_at,
        Decimal('0.00'),
        Decimal('0.00'),
        Decimal('0.00'),
        Decimal('0.00'),
        Decimal('0.00'),
        Decimal('0.00'),
        Decimal('0.00'),
    )
    assert saved is True
    assert cut_id is not None


def test_historical_sale_keeps_snapshots_after_catalog_changes(pos_catalog):
    success, _, sale = procesar_venta_completa(
        'Cliente snapshot',
        '8',
        [{
            'id': pos_catalog['product_id'],
            'variante_id': pos_catalog['variant_id'],
            'cantidad': 1,
        }],
        total='60.00',
        metodo_pago_id=2,
        usuario_actual=pos_catalog['marker'],
    )
    assert success is True
    assert actualizar_estado_orden(sale['venta_id'], 2) is True
    assert actualizar_estado_orden(sale['venta_id'], 4) is True

    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tproductos SET nombre_producto = 'Nombre nuevo', precio = 999.00 "
                'WHERE Id = %s',
                (pos_catalog['product_id'],),
            )
            cursor.execute(
                "UPDATE ttamanos SET tamano = 'Tamaño nuevo' WHERE Id = %s",
                (pos_catalog['size_id'],),
            )
            cursor.execute(
                'UPDATE tproductos_variantes SET precio = 888.00 WHERE Id = %s',
                (pos_catalog['variant_id'],),
            )
        connection.commit()
    finally:
        connection.close()

    _, details = obtener_venta_completa(sale['venta_id'])

    assert len(details) == 1
    assert details[0]['nombre_producto'] == 'Café de integración'
    assert details[0]['tamano'] == pos_catalog['marker']
    assert details[0]['precio'] == Decimal('60.00')
    assert details[0]['subtotal'] == Decimal('60.00')
