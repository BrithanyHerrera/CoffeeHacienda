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

```bash
pip install -r requirements.txt
```

Crear un archivo `bd.env` con las credenciales (ver `bd.env.example`).

```bash
python app.py
```

Arranca en `http://localhost:5000`.

## Variables de entorno (`bd.env`)

```
APP_ENV=LOCAL

DB_HOST_LOCAL=localhost
DB_PORT_LOCAL=3307
DB_USER_LOCAL=root
DB_PASS_LOCAL=
DB_NAME_LOCAL=bd

SECRET_KEY=tu_clave_secreta
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=correo@gmail.com
MAIL_PASSWORD=contraseña_de_app
```

---
Coffee Hacienda 🤎
