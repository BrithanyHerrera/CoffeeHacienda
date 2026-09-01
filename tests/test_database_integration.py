import os

import pytest

from bd import Conexion_BD


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv('RUN_DB_TESTS') != '1',
        reason='RUN_DB_TESTS=1 habilita las pruebas de lectura con MySQL',
    ),
]


def test_required_schema_versions_are_applied():
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT version FROM tschema_migrations ORDER BY version')
            versions = [row['version'] for row in cursor.fetchall()]
            assert versions[-3:] == [2, 3, 4]
    finally:
        connection.close()


def test_required_schema_columns_exist():
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            expected_columns = {
                ('tmetodospago', 'codigo'),
                ('tdetalleventas', 'producto_nombre_snapshot'),
                ('tdetalleventas', 'tamano_snapshot'),
                ('tventas', 'motivo_cancelacion'),
                ('tmovimientosinventario', 'venta_id'),
                ('tusuarios', 'sesion_version'),
                ('tauditoria', 'accion'),
            }
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
            """)
            actual_columns = {
                (row['TABLE_NAME'], row['COLUMN_NAME'])
                for row in cursor.fetchall()
            }
            assert expected_columns <= actual_columns
    finally:
        connection.close()
