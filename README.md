Coffee Hacienda - Sistema de Punto de Venta (POS)
==================================================

Sistema de punto de venta y administracion para cafeteria desarrollado con Flask y MySQL.

Tecnologias utilizadas:
- Python 3.12 / Flask (estructura con Blueprints)
- MySQL 8.0 (soporte local y nube Aiven con SSL)
- DBUtils (pool de conexiones)
- HTML, CSS y JavaScript
- Pytest y Ruff (pruebas y revision de codigo)

Estructura del proyecto:
- app.py: punto de entrada y configuracion de la aplicacion
- bd.py: conexion y pool a la base de datos MySQL
- utils.py: decoradores de sesion, roles y validaciones
- extensions.py: extensiones de seguridad, rate limit y correo
- blueprints/: controladores y rutas del sistema (ventas, usuarios, productos, inventario, finanzas)
- models/: modelos y consultas SQL a la base de datos
- templates/: plantillas HTML de las pantallas
- static/: estilos CSS, scripts JS e imagenes
- docs/: documentacion del proyecto y actividades academicas
- tests/: pruebas unitarias del sistema (290 pruebas)

Instalacion y puesta en marcha:
1. Clonar el repositorio en la computadora.
2. Ejecutar instalar_dependencias.bat (crea automaticamente el entorno .venv e instala las librerias).
3. Copiar el archivo bd.env.example, renombrarlo como bd.env y poner las credenciales de tu base de datos y correo.
4. Para arrancar el sistema, hacer doble clic en iniciar_sistema.bat o correr:
   python app.py
5. Entrar desde el navegador a: http://localhost:5000

Base de datos:
Para crear la base de datos desde cero, importar el archivo database/db.sql en MySQL. Este archivo ya trae la estructura completa de tablas y datos iniciales.

Si necesitas crear un usuario administrador desde consola:
.venv\Scripts\python.exe scripts/create_admin.py --username admin --email admin@example.com

Pruebas y calidad de codigo:
Para correr las pruebas unitarias localmente:
.venv\Scripts\python.exe -m pytest -m "not integration" --cov

Para revisar la sintaxis y estilo con el linter:
.venv\Scripts\python.exe -m ruff check .

Nota: En GitHub Actions se ejecutan estas mismas pruebas de forma automatica en cada push a la rama main.
