from pathlib import Path

from scripts.apply_migrations import discover_migrations, split_sql


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_divisor_sql_preserva_punto_y_coma_dentro_de_cadenas():
    statements = split_sql("SET @x = 'a;b'; SELECT 1;")

    assert statements == ["SET @x = 'a;b'", 'SELECT 1']


def test_migraciones_estan_numeradas_y_son_unicas():
    migrations = discover_migrations()
    versions = [version for version, _ in migrations]

    assert versions == sorted(set(versions))
    assert versions[-2:] == [3, 4]


def test_volcado_esquema_actual_no_contiene_usuarios_ni_correos_operativos():
    schema = (
        PROJECT_ROOT / 'database' / 'db.sql'
    ).read_text(encoding='utf-8-sig').lower()

    assert 'insert into `tusuarios`' not in schema
    assert '@gmail.com' not in schema
    assert 'datos operativos de tusuarios omitidos intencionalmente' in schema


def test_volcado_esquema_actual_es_una_linea_base_completa_y_versionada():
    schema = (
        PROJECT_ROOT / 'database' / 'db.sql'
    ).read_text(encoding='utf-8-sig').lower()

    assert 'create table `tschema_migrations`' in schema
    assert "(2, 'ventas_variantes_cancelacion')" in schema
    assert "(3, 'estabilidad_auditoria')" in schema
    assert "(4, 'auditoria_operaciones')" in schema
