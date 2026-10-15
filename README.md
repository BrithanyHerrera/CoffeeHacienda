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
- app.py: punto de entrada, carga de variables (.env/bd.env) y auto-relanzamiento en .venv
- bd.py: conexion y pool a la base de datos MySQL
- utils.py: decoradores de sesion, roles y validaciones
- extensions.py: extensiones de seguridad, rate limit y correo
- blueprints/: controladores y rutas del sistema (ventas, usuarios, productos, inventario, finanzas)
- models/: modelos y consultas SQL a la base de datos
- templates/: plantillas HTML de las pantallas
- static/: estilos CSS, scripts JS e imagenes
- docs/: documentacion del proyecto y actividades academicas
- tests/: pruebas unitarias del sistema (290 pruebas)

Instalacion de dependencias:
Para instalar todo lo que el sistema necesita, hay dos opciones:

Opcion 1 (Automatica y recomendada):
Dar doble clic al archivo instalar_dependencias.bat
Este script hace todo solo:
1. Revisa que Python este instalado en el equipo.
2. Crea la carpeta del entorno virtual (.venv) si todavia no existe.
3. Actualiza pip a la version mas reciente.
4. Instala todas las dependencias del proyecto (requirements.txt y requirements-dev.txt).

Opcion 2 (Manual por consola):
Abrir la terminal en la carpeta del proyecto y ejecutar:
py -3.12 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt

Configuracion inicial:
1. Copiar el archivo bd.env.example y renombrarlo como bd.env.
2. Abrir bd.env con un editor de texto y poner los datos de conexion de tu base de datos (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME) y tu SECRET_KEY.
3. Para la base de datos, importar el archivo database/db.sql en MySQL (por ejemplo usando phpMyAdmin, MySQL Workbench o MAMP). Este archivo ya trae todas las tablas y datos requeridos.
4. Si necesitas crear un usuario administrador desde la terminal:
   .venv\Scripts\python.exe scripts/create_admin.py --username admin --email admin@example.com

Pasos para ejecutar el sistema:
El archivo app.py ya esta programado para detectar y usar el entorno virtual automaticamente. Esto significa que si lo ejecutas con el Python normal de Windows, app.py detecta si existe la carpeta .venv y se relanza solo dentro de ella, ademas de cargar las variables de bd.env y .env.

Tienes tres opciones para iniciarlo:

Opcion A (La mas comoda):
Dar doble clic al archivo iniciar_sistema.bat
(Abre la consola y levanta el servidor directamente con el entorno virtual).

Opcion B (Comando directo):
python app.py
(El propio app.py detecta .venv y lo ejecuta de forma transparente).

Opcion C (Activando el entorno manualmente):
.\.venv\Scripts\activate
python app.py

Una vez iniciado el servidor, abrir el navegador web e ingresar a:
http://localhost:5000

Pruebas y calidad de codigo:
Para correr las pruebas unitarias localmente:
.venv\Scripts\python.exe -m pytest -m "not integration" --cov

Para revisar la sintaxis y estilo con el linter:
.venv\Scripts\python.exe -m ruff check .

Nota: En GitHub Actions se ejecutan estas mismas pruebas de forma automatica en cada push a la rama main.
