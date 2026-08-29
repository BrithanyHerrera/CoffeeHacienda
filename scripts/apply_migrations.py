"""Aplica migraciones SQL numeradas y registra su versión."""
import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from bd import Conexion_BD  # noqa: E402


MIGRATION_PATTERN = re.compile(r'^(\d+)_.*\.sql$')


def split_sql(script):
    """Separa sentencias respetando cadenas y comentarios SQL de una línea."""
    statements = []
    buffer = []
    quote = None
    escaped = False
    index = 0

    while index < len(script):
        char = script[index]
        next_char = script[index + 1] if index + 1 < len(script) else ''

        if quote:
            buffer.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                if next_char == quote:
                    buffer.append(next_char)
                    index += 1
                else:
                    quote = None
        elif char in ("'", '"', '`'):
            quote = char
            buffer.append(char)
        elif char == '-' and next_char == '-':
            while index < len(script) and script[index] not in '\r\n':
                index += 1
            buffer.append('\n')
        elif char == ';':
            statement = ''.join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
        else:
            buffer.append(char)
        index += 1

    statement = ''.join(buffer).strip()
    if statement:
        statements.append(statement)
    return statements


def discover_migrations():
    migrations_dir = PROJECT_ROOT / 'migrations'
    migrations = []
    for path in migrations_dir.glob('*.sql'):
        match = MIGRATION_PATTERN.match(path.name)
        if match:
            migrations.append((int(match.group(1)), path))
    return sorted(migrations)


def ensure_tracking_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tschema_migrations (
            version INT NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            aplicado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (version)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)


def apply_migrations(dry_run=False):
    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            if dry_run:
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'tschema_migrations'
                """)
                tracking_exists = cursor.fetchone()['total'] > 0
                if tracking_exists:
                    cursor.execute('SELECT version FROM tschema_migrations')
                    applied = {row['version'] for row in cursor.fetchall()}
                else:
                    applied = set()
            else:
                ensure_tracking_table(cursor)
                connection.commit()
                cursor.execute('SELECT version FROM tschema_migrations')
                applied = {row['version'] for row in cursor.fetchall()}

            pending = [item for item in discover_migrations() if item[0] not in applied]
            if dry_run:
                return [path.name for _, path in pending]

            completed = []
            for version, path in pending:
                script = path.read_text(encoding='utf-8-sig')
                try:
                    for statement in split_sql(script):
                        cursor.execute(statement)
                    connection.commit()
                    completed.append(path.name)
                except Exception:
                    connection.rollback()
                    raise RuntimeError(f'Falló la migración {path.name}')
            return completed
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Muestra las migraciones pendientes sin aplicarlas.',
    )
    args = parser.parse_args()
    migrations = apply_migrations(dry_run=args.dry_run)
    if migrations:
        action = 'Pendientes' if args.dry_run else 'Aplicadas'
        print(f'{action}: {", ".join(migrations)}')
    else:
        print('No hay migraciones pendientes.')


if __name__ == '__main__':
    main()
