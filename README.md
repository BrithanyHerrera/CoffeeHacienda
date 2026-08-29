# Coffee Hacienda ☕

Sistema de punto de venta y gestión para cafetería.

## Tecnologías

- **Backend:** Python + Flask (Blueprints)
- **Base de datos:** MySQL 8 (local y Aiven)
- **Pool de conexiones:** DBUtils
- **Frontend:** HTML5, CSS3, JavaScript
- **Reportes:** jsPDF

## Estructura

```
app.py              → Punto de entrada
bd.py               → Pool de conexiones MySQL
utils.py            → Decoradores y validaciones
extensions.py       → Rate limiter y CSRF
blueprints/         → Controladores (rutas HTTP)
models/             → Acceso a base de datos
templates/          → Vistas (Jinja2)
static/css/         → Estilos
static/js/          → Scripts del frontend
static/images/      → Imágenes de productos
```

## Instalación

Requiere Python 3.12 y MySQL 8.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Crear `bd.env` a partir de `bd.env.example`. El repositorio no contiene
credenciales ni usuarios reales.

Para una base nueva, importar primero `bd.sql`. Para una base existente o
recién importada, revisar y aplicar las migraciones pendientes:

```powershell
python scripts/apply_migrations.py --dry-run
python scripts/apply_migrations.py
```

Crear el primer administrador solicitando la contraseña de forma interactiva:

```powershell
python scripts/create_admin.py --username admin --email admin@example.com
```

Arranque local:

```powershell
python app.py
```

Arranca en `http://localhost:5000`.

En producción, usar un servidor WSGI y un proxy HTTPS. Ejemplo con Waitress:

```powershell
waitress-serve --call --listen=127.0.0.1:8000 app:create_app
```

## Variables de entorno (`bd.env`)

```
APP_ENV=LOCAL

DB_HOST=localhost
DB_PORT=3306
DB_USER=coffee_hacienda
DB_PASSWORD=reemplazar
DB_NAME=coffee_hacienda

SECRET_KEY=tu_clave_secreta
RATELIMIT_STORAGE_URI=memory://
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=correo@gmail.com
MAIL_PASSWORD=contraseña_de_app
```

Para Aiven, usar `APP_ENV=NUBE`, los valores `DB_*` del servicio y la ruta
local de su certificado en `DB_SSL_CA`. Antes de migrar Aiven:

1. Detener temporalmente escrituras en la aplicación.
2. Crear y verificar un respaldo.
3. Ejecutar `--dry-run` y aplicar las migraciones.
4. Desplegar la misma revisión del código.
5. Comprobar `/health`, login, una venta de prueba y los logs.

No se debe aplicar la migración 002 por separado mientras una versión antigua
de la aplicación siga atendiendo ventas.

---
Coffee Hacienda 🤎
