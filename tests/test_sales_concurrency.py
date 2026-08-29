import os
import threading
from decimal import Decimal

import pytest

from bd import Conexion_BD
from models.modelsVentas import procesar_venta_completa

pytestmark = pytest.mark.integration

@pytest.mark.skipif(
    os.getenv('RUN_DB_WRITE_TESTS') != '1',
    reason='RUN_DB_WRITE_TESTS=1 habilita pruebas de escritura en una base separada'
)
def test_concurrencia_ventas_mismo_producto_evita_stock_negativo():
    """
    Simula dos hilos (dos meseros) intentando vender el mismo producto
    exactamente al mismo tiempo. Valida que MySQL procesa las transacciones
    de forma atómica y el stock no quede negativo, o que al menos una falle.
    """
    connection = Conexion_BD()

    with connection.cursor() as cursor:
        cursor.execute('SELECT DATABASE() AS nombre')
        database_name = cursor.fetchone()['nombre']
    if not database_name.lower().endswith('_test'):
        connection.close()
        pytest.skip('La prueba de escritura exige una base cuyo nombre termine en _test')
    
    # Preparar datos de prueba
    try:
        with connection.cursor() as cursor:
            # Crear un producto temporal con stock de 1
            cursor.execute("""
                INSERT INTO tproductos (nombre_producto, categoria_id, descripcion, precio, stock, imagen, requiere_inventario, status)
                VALUES ('Café Concurrente', 1, 'Prueba race condition', 50.00, 1, NULL, 1, 'Activo')
            """)
            producto_id = cursor.lastrowid
        connection.commit()
    except Exception as e:
        pytest.skip(f"No se pudo preparar la base de datos de prueba: {e}")

    resultados = []
    
    def intento_de_venta(hilo_id):
        # Cada hilo intenta comprar 1 unidad (quedan 1 en total)
        productos = [{'id': producto_id, 'cantidad': 1}]
        exito, mensaje, datos = procesar_venta_completa(
            cliente=f"Cliente Hilo {hilo_id}",
            mesa="1",
            productos=productos,
            total=Decimal("50.00"),
            metodo_pago_id=1,
            usuario_actual="vendedor_test",
            dinero_recibido="50.00",
            cambio="0.00"
        )
        resultados.append((exito, mensaje))

    # Iniciar los dos hilos casi simultáneamente
    hilo1 = threading.Thread(target=intento_de_venta, args=(1,))
    hilo2 = threading.Thread(target=intento_de_venta, args=(2,))
    
    hilo1.start()
    hilo2.start()
    
    hilo1.join()
    hilo2.join()
    
    # Limpiar el producto de prueba
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT stock FROM tproductos WHERE Id = %s", (producto_id,))
            stock_final = cursor.fetchone()['stock']
            # Borrar las ventas de prueba si se crearon (cascade o manual)
            cursor.execute("DELETE FROM tproductos WHERE Id = %s", (producto_id,))
        connection.commit()
    finally:
        connection.close()

    # Resultados esperados: 
    # Solo una venta debió tener éxito, la otra debió fallar por stock insuficiente
    ventas_exitosas = sum(1 for exito, _ in resultados if exito)
    ventas_fallidas = sum(1 for exito, _ in resultados if not exito)

    assert ventas_exitosas == 1, "Solo una venta debió procesarse exitosamente"
    assert ventas_fallidas == 1, "La otra venta debió fallar por falta de inventario"
    assert stock_final == 0, "El inventario nunca debe quedar en números negativos"
