# Base de datos de Coffee Hacienda

## Instalación nueva

Importar únicamente `db.sql`. Contiene el esquema completo y las
versiones 002, 003 y 004 ya incorporadas. No se ejecutan migraciones después de
una instalación nueva.

## Base existente con datos

No importar nuevamente `db.sql`, porque reemplaza las tablas.
Crear un respaldo y ejecutar desde la raíz del proyecto:

```powershell
python scripts/apply_migrations.py --dry-run
python scripts/apply_migrations.py
```

El programa utiliza los archivos de `database/migraciones` y aplica solamente
las versiones pendientes, en orden numérico.

## Organización

- `db.sql`: esquema completo para instalaciones nuevas.
- `migraciones/`: cambios incrementales para bases existentes.
