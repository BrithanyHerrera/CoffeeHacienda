"""Crea una base MySQL temporal, ejecuta pruebas de escritura y la elimina."""
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from pymysql.constants import CLIENT


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_PATTERN = re.compile(r'^coffee_hacienda_codex_[0-9a-f]{8}_test$')


def _setting(name, legacy_name):
    return os.getenv(name) or os.getenv(f'{legacy_name}_LOCAL')


def _execute_script(connection, path):
    sql = path.read_text(encoding='utf-8')
    with connection.cursor() as cursor:
        cursor.execute(sql)
        while cursor.nextset():
            pass


def main():
    load_dotenv(PROJECT_ROOT / 'bd.env')
    database_name = f'coffee_hacienda_codex_{secrets.token_hex(4)}_test'
    if not TEST_DATABASE_PATTERN.fullmatch(database_name):
        raise RuntimeError('El nombre de la base temporal no es seguro')

    connection_args = {
        'host': _setting('DB_HOST', 'DB_HOST'),
        'port': int(_setting('DB_PORT', 'DB_PORT') or '3306'),
        'user': _setting('DB_USER', 'DB_USER'),
        'password': _setting('DB_PASSWORD', 'DB_PASS'),
        'charset': 'utf8mb4',
        'autocommit': True,
        'client_flag': CLIENT.MULTI_STATEMENTS,
    }
    if not all((connection_args['host'], connection_args['user'], connection_args['password'])):
        raise RuntimeError('La configuración MySQL local está incompleta')

    admin_connection = pymysql.connect(**connection_args)
    try:
        with admin_connection.cursor() as cursor:
            cursor.execute(
                f'CREATE DATABASE `{database_name}` '
                'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
            )

        test_connection = pymysql.connect(database=database_name, **connection_args)
        try:
            _execute_script(test_connection, PROJECT_ROOT / 'bd.sql')
            _execute_script(
                test_connection,
                PROJECT_ROOT / 'migrations' / '002_ventas_variantes_cancelacion.sql',
            )
            _execute_script(
                test_connection,
                PROJECT_ROOT / 'migrations' / '003_estabilidad_auditoria.sql',
            )
        finally:
            test_connection.close()

        test_environment = os.environ.copy()
        test_environment.update(
            APP_ENV='TESTING',
            DB_HOST=connection_args['host'],
            DB_PORT=str(connection_args['port']),
            DB_USER=connection_args['user'],
            DB_PASSWORD=connection_args['password'],
            DB_NAME=database_name,
            RUN_DB_TESTS='1',
            RUN_DB_WRITE_TESTS='1',
        )
        result = subprocess.run(
            [
                sys.executable,
                '-m',
                'pytest',
                'tests/test_database_integration.py',
                'tests/test_pos_flow_integration.py',
                'tests/test_sales_concurrency.py',
                '-m',
                'integration',
            ],
            cwd=PROJECT_ROOT,
            env=test_environment,
            check=False,
        )
        return result.returncode
    finally:
        with admin_connection.cursor() as cursor:
            cursor.execute(f'DROP DATABASE IF EXISTS `{database_name}`')
        admin_connection.close()


if __name__ == '__main__':
    raise SystemExit(main())
