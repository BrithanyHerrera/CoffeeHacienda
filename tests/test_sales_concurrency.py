import os
import secrets
import threading
from decimal import Decimal

import pytest

from bd import Conexion_BD
from models.modelsVentas import procesar_venta_completa


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv('RUN_DB_WRITE_TESTS') != '1',
        reason='RUN_DB_WRITE_TESTS=1 habilita pruebas en una base aislada',
    ),
]


def test_concurrent_sales_never_leave_negative_stock():
    marker = f'concurrente_{secrets.token_hex(6)}'
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT DATABASE() AS nombre')
            database_name = cursor.fetchone()['nombre']
            assert database_name.lower().endswith('_test')
            cursor.execute(
                'INSERT INTO tusuarios (usuario, contrasena, correo, rol_id) '
                'VALUES (%s, %s, %s, 2)',
                (marker, 'hash-no-utilizado', f'{marker}@example.test'),
            )
            user_id = cursor.lastrowid
            cursor.execute(
                'INSERT INTO tcategorias (categoria, requiere_inventario) VALUES (%s, 1)',
                (marker,),
            )
            category_id = cursor.lastrowid
            cursor.execute(
                '''
                INSERT INTO tproductos
                    (nombre_producto, descripcion, precio, stock, stock_minimo,
                     stock_maximo, categoria_id, activo)
                VALUES (%s, 'Prueba concurrente', 50.00, 1, 1, 10, %s, 1)
                ''',
                (marker, category_id),
            )
            product_id = cursor.lastrowid
        connection.commit()
    finally:
        connection.close()

    barrier = threading.Barrier(2)
    result_lock = threading.Lock()
    results = []
    errors = []

    def attempt_sale(thread_id):
        try:
            barrier.wait(timeout=5)
            result = procesar_venta_completa(
                nombre_cliente=f'Cliente concurrente {thread_id}',
                numero_mesa='1',
                productos=[{'id': product_id, 'cantidad': 1}],
                total=Decimal('0.01'),
                metodo_pago_id=1,
                usuario_actual=marker,
                dinero_recibido='50.00',
                cambio='999.00',
            )
            with result_lock:
                results.append(result)
        except Exception as error:
            with result_lock:
                errors.append(error)

    threads = [threading.Thread(target=attempt_sale, args=(index,)) for index in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert all(not thread.is_alive() for thread in threads)
    assert errors == []
    assert len(results) == 2
    assert sum(1 for success, _, _ in results if success) == 1
    assert sum(1 for success, _, _ in results if not success) == 1

    verification = Conexion_BD()
    try:
        with verification.cursor() as cursor:
            cursor.execute('SELECT stock FROM tproductos WHERE Id = %s', (product_id,))
            assert cursor.fetchone()['stock'] == 0
            cursor.execute(
                'SELECT COUNT(*) AS total FROM tventas WHERE vendedor_id = %s',
                (user_id,),
            )
            assert cursor.fetchone()['total'] == 1
            cursor.execute(
                'SELECT COUNT(*) AS total FROM tmovimientosinventario '
                'WHERE producto_id = %s AND tipo_movimiento_id = 2',
                (product_id,),
            )
            assert cursor.fetchone()['total'] == 1
    finally:
        verification.close()
