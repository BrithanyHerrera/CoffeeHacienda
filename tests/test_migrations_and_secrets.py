from pathlib import Path

from scripts.apply_migrations import discover_migrations, split_sql


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_sql_splitter_preserves_semicolon_inside_string():
    statements = split_sql("SET @x = 'a;b'; SELECT 1;")

    assert statements == ["SET @x = 'a;b'", 'SELECT 1']


def test_migrations_are_numbered_and_unique():
    migrations = discover_migrations()
    versions = [version for version, _ in migrations]

    assert versions == sorted(set(versions))
    assert versions[-2:] == [3, 4]


def test_current_schema_dump_has_no_operational_users_or_emails():
    schema = (PROJECT_ROOT / 'bd.sql').read_text(encoding='utf-8-sig').lower()

    assert 'insert into `tusuarios`' not in schema
    assert '@gmail.com' not in schema
    assert 'datos operativos de tusuarios omitidos intencionalmente' in schema
