# 🛠️ Manual Técnico y de Mantenimiento — Coffee Hacienda POS

> **Versión:** 1.0  
> **Fecha:** Noviembre 2026  
> **Sistema:** Coffee Hacienda POS  
> **Audiencia:** Desarrolladores, Administradores de Sistemas y Personal de Mantenimiento

---

## 📖 Tabla de Contenidos

1. [Introducción y Stack Tecnológico](#-introducción-y-stack-tecnológico)
2. [Requisitos del Sistema](#1-requisitos-del-sistema)
3. [Instalación Inicial Paso a Paso](#2-instalación-inicial-paso-a-paso)
4. [Configuración de Variables de Entorno (bd.env)](#3-configuración-de-variables-de-entorno-bdenv)
5. [Arquitectura del Software](#4-arquitectura-del-software)
6. [Base de Datos y Entorno Dual MySQL](#5-base-de-datos-y-entorno-dual-mysql)
7. [Pool de Conexiones (bd.py)](#6-pool-de-conexiones-bdpy)
8. [Seguridad, Autenticación y Autorización](#7-seguridad-autenticación-y-autorización)
9. [Catálogo de Blueprints y Rutas API](#8-catálogo-de-blueprints-y-rutas-api)
10. [Suite de Pruebas Automatizadas (pytest)](#9-suite-de-pruebas-automatizadas-pytest)
11. [Gestión y Almacenamiento de Archivos](#10-gestión-y-almacenamiento-de-archivos)
12. [Despliegue en Producción y Nube (Aiven)](#11-despliegue-en-producción-y-nube-aiven)
13. [Control de Versiones y Flujo Git](#12-control-de-versiones-y-flujo-git)
14. [Directrices para Agentes de IA (AGENTS.md)](#13-directrices-para-agentes-de-ia-agentsmd)
15. [Guía de Solución de Problemas (Troubleshooting)](#14-guía-de-solución-de-problemas-troubleshooting)

---

## 🚀 Introducción y Stack Tecnológico

**Coffee Hacienda POS** es una aplicación web empresarial orientada a la gestión operativa, comercial y contable de cafeterías. Diseñada con un enfoque modular y arquitectura desacoplada, implementa el patrón **Application Factory** de Flask junto con separación de dominios mediante **Blueprints**.

### 💻 Componentes del Stack

| Capa | Tecnología | Propósito |
|---|---|---|
| **Lenguaje Backend** | Python 3.12+ | Lógica de negocio, controladores y endpoints |
| **Framework Web** | Flask 3.0+ | Enrutamiento HTTP, renderizado de plantillas y API REST |
| **Motor de Base de Datos** | MySQL 8.0+ / MAMP / Aiven | Persistencia relacional, transacciones ACID |
| **Pool de Conexiones** | DBUtils (`PooledDB`) + PyMySQL | Reutilización de sockets de conexión de alta eficiencia |
| **Seguridad Web** | Flask-WTF (CSRF) + Flask-Limiter | Protección contra falsificación de peticiones y DoS/fuerza bruta |
| **Criptografía** | Werkzeug Security | Hashing de contraseñas mediante PBKDF2:SHA256 |
| **Plantillas** | Jinja2 + HTML5 semántico | Renderizado del lado del servidor (SSR) |
| **Frontend UI** | Bootstrap 5 + Vanilla JavaScript | Interfaz responsiva, componentes modulares y eventos |
| **Generación de PDFs** | jsPDF + AutoTable | Construcción de tickets de venta y comprobantes de corte |
| **Servicio de Correo** | Flask-Mail (SMTP/TLS) | Notificaciones y flujo de recuperación de accesos |
| **Pruebas y Calidad** | pytest + Ruff | Suite de pruebas unitarias/integración y linter estático |

---

## 1. Requisitos del Sistema

### 1.1 Entorno de Desarrollo y Servidor Local

| Componente | Requisito Mínimo | Recomendado |
|---|---|---|
| **Sistema Operativo** | Windows 10/11, macOS 12+, Ubuntu 22.04 LTS | Windows 11 / Linux Server |
| **Python** | 3.12.0 x64 | 3.12.4+ |
| **MySQL Server** | MySQL 5.7+ o MariaDB 10.4+ | MySQL 8.0 Community / MAMP |
| **RAM** | 4 GB | 8 GB o superior |
| **Almacenamiento** | 2 GB libres en disco | SSD con al menos 10 GB |
| **Navegador** | Google Chrome 110+, Mozilla Firefox 115+, Edge 110+ | Google Chrome / Edge actualizado |

---

## 2. Instalación Inicial Paso a Paso

Sigue estas instrucciones para desplegar el entorno de desarrollo local desde cero en un equipo con Windows:

### Paso 1: Clonar el Repositorio de Código
```bash
git clone https://github.com/BrithanyHerrera/CoffeeHacienda.git
cd CoffeeHacienda
```

### Paso 2: Crear el Entorno Virtual de Python
```bash
python -m venv .venv
```

### Paso 3: Activar el Entorno Virtual
En Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```
En Windows (CMD):
```cmd
.\.venv\Scripts\activate.bat
```

> [!TIP]
> El punto de entrada `app.py` incluye detección automática: si se ejecuta con el Python global de Windows, se relanza automáticamente dentro de `.venv/Scripts/python.exe`.

### Paso 4: Instalar las Dependencias
```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```
*(Si solo se requiere entorno de ejecución sin suites de prueba, instalar `requirements.txt`).*

### Paso 5: Configurar el Archivo de Entorno (`bd.env`)
Copiar la plantilla de ejemplo y crear el archivo local de variables de entorno:
```bash
copy bd.env.example bd.env
```
Abrir `bd.env` y configurar las credenciales de base de datos local y la clave secreta `SECRET_KEY`.

### Paso 6: Configurar e Inicializar la Base de Datos Local
1. Iniciar **MAMP** (o servicio MySQL local) asegurando que el puerto `3306` esté activo.
2. Abrir phpMyAdmin o la consola de MySQL y crear la base de datos:
```sql
CREATE DATABASE bd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
3. Importar el esquema base:
```bash
mysql -u root -p bd < database/db.sql
```

### Paso 7: Crear el Primer Usuario Administrador
Ejecutar el script automatizado para dar de alta al superusuario inicial:
```bash
python scripts/create_admin.py --username admin --email admin@coffeehacienda.com
```
El script solicitará ingresar y confirmar la contraseña segura del administrador.

### Paso 8: Iniciar el Servidor de Desarrollo
Puedes hacer doble clic en `iniciar_sistema.bat` o iniciar directamente desde terminal:
```bash
python app.py
```
Abrir el navegador web en: **`http://127.0.0.1:5000`**

---

## 3. Configuración de Variables de Entorno (`bd.env`)

La configuración global del sistema se administra a través del archivo `bd.env`. Este archivo contiene credenciales sensibles y **está explícitamente ignorado en `.gitignore`**.

> [!CAUTION]
> **NUNCA subas `bd.env` a Git.** Si necesitas documentar nuevas variables de entorno, agrégalas con valores ficticios en `bd.env.example`.

### Matriz Completa de Variables

| Variable | Tipo | Descripción | Ejemplo / Valor por Defecto | ¿Obligatoria? |
|---|---|---|---|:---:|
| `APP_ENV` | String | Entorno de ejecución (`LOCAL`, `NUBE`, `PRODUCTION`, `TESTING`) | `LOCAL` | Sí |
| `SECRET_KEY` | String | Clave criptográfica para firmas de sesión y tokens CSRF | Clave aleatoria de 64 caracteres | Sí |
| `FLASK_DEBUG` | Boolean | Habilita el debugger interactivo y recarga en caliente | `False` en producción, `True` en local | Sí |
| `MAX_CONTENT_LENGTH_MB` | Integer | Límite máximo en Megabytes para peticiones HTTP entrantes (ej. subida de imágenes) | `8` | No (def. 8) |
| `SESSION_VALIDATION_INTERVAL_SECONDS` | Integer | Intervalo de re-validación de vigencia de sesión en BD | `60` | No (def. 60) |
| `RATELIMIT_STORAGE_URI` | URI | Backend de almacenamiento de cuotas del Rate Limiter (`memory://` o `redis://`) | `memory://` (local) / `redis://...` | Sí |
| `TRUST_PROXY` | Boolean | Habilita el middleware `ProxyFix` para leer IPs y protocolos reales tras un Reverse Proxy | `False` (local) / `True` (nube) | Sí |
| `DB_HOST` | String | Dirección o hostname del servidor MySQL activo | `127.0.0.1` | Sí |
| `DB_PORT` | Integer | Puerto de conexión a MySQL | `3306` | Sí |
| `DB_USER` | String | Usuario con permisos en la base de datos | `root` / `coffee_hacienda` | Sí |
| `DB_PASSWORD` | String | Contraseña del usuario de base de datos | `tu_password` | Sí |
| `DB_NAME` | String | Nombre de la base de datos activa | `bd` / `coffee_hacienda` | Sí |
| `DB_SSL_CA` | FilePath | Ruta absoluta al certificado CA (`.pem`) de Aiven | `C:/certificados/ca.pem` | Solo en `NUBE` |
| `MAIL_SERVER` | String | Host del servidor SMTP para envío de correos | `smtp.gmail.com` | Sí |
| `MAIL_PORT` | Integer | Puerto del servidor SMTP | `587` | Sí |
| `MAIL_USE_TLS` | Boolean | Activa cifrado STARTTLS para correo | `True` | Sí |
| `MAIL_USERNAME` | Email | Cuenta de correo emisora | `notificaciones@coffeehacienda.com` | Sí |
| `MAIL_PASSWORD` | String | Contraseña de aplicación SMTP | `xxxx xxxx xxxx xxxx` | Sí |

---

## 4. Arquitectura del Software

El proyecto sigue una arquitectura modular desacoplada basada en el patrón **Application Factory**.

### 4.1 Árbol de Directorios del Proyecto

```
CoffeeHacienda/
├── app.py                      # Fábrica de aplicación (create_app) y punto de entrada
├── bd.py                       # Gestor del Pool de conexiones MySQL (DBUtils PooledDB)
├── config.py                   # Configuraciones por entorno (LocalConfig, ProductionConfig)
├── extensions.py               # Instancias compartidas (limiter, csrf, mail)
├── utils.py                    # Decoradores (@login_required, @admin_required) y utilidades
├── blueprints/                 # Controladores y rutas agrupados por dominio
│   ├── autenticacion_bp.py     # Login, logout, recuperación de contraseña
│   ├── finanzas_bp.py          # Cortes de caja, exportación Excel, reportes
│   ├── generales_bp.py         # Healthcheck, guardado de tickets PDF, bienvenida
│   ├── inventario_bp.py        # Control de existencias, ajustes con motivo
│   ├── productos_bp.py         # Catálogo de productos, categorías, imágenes
│   ├── usuarios_bp.py          # Administración de personal, altas, bajas, roles
│   └── ventas_bp.py            # POS Menú, pedidos, órdenes, historial y exportación
├── models/                     # Capa de acceso a datos y consultas parametrizadas
│   ├── modelsCorteCaja.py
│   ├── modelsHistorial.py
│   ├── modelsInventario.py
│   ├── modelsOrdenes.py
│   ├── modelsProductos.py
│   ├── modelsReporteFinanciero.py
│   ├── modelsUsuarios.py
│   └── modelsVentas.py
├── templates/                  # Plantillas HTML renderizadas con Jinja2
│   ├── bienvenida.html
│   ├── corteCaja.html
│   ├── gestionProductos.html
│   ├── gestionUsuarios.html
│   ├── historial.html
│   ├── inventario.html
│   ├── login.html
│   ├── menu.html
│   ├── ordenes.html
│   ├── recuperar.html
│   └── reportesFinancieros.html
├── static/                     # Archivos estáticos de cliente
│   ├── css/                    # Hojas de estilo modulares
│   ├── js/                     # Scripts clientes (menu.js, inventario.js, etc.)
│   └── images/productos/       # Imágenes subidas de productos
├── database/                   # Definición de esquema y migraciones
│   ├── db.sql                  # Esquema completo de la base de datos
│   └── migraciones/            # Scripts SQL versionados (001_..., 002_...)
├── scripts/                    # Scripts administrativos y de soporte
│   ├── apply_migrations.py     # Aplicador automático de migraciones
│   └── create_admin.py         # Alta de administrador vía CLI
├── tests/                      # Suite de pruebas automatizadas con pytest
│   ├── conftest.py             # Fixtures de Flask y mocks
│   └── db_fakes.py             # Conexiones simuladas a BD para pruebas unitarias
├── instance/pdfs/              # Almacén de comprobantes PDF (gitignored)
│   ├── tickets_ventas/         # Tickets de venta generados silenciosamente
│   └── cortes_de_caja/         # Resguardos de cortes de caja
├── docs/                       # Documentación formal del proyecto
│   ├── MANUAL_USUARIO.md       # Guía de usuario final
│   └── MANUAL_TECNICO.md       # Guía de arquitectura y desarrollo (este documento)
├── bd.env                      # Secretos del entorno activo (gitignored)
├── bd.env.example              # Plantilla pública de variables
└── AGENTS.md                   # Reglas de negocio e integridad para agentes IA
```

---

## 5. Base de Datos y Entorno Dual MySQL

El sistema cuenta con soporte bidireccional para dos entornos de persistencia:
1. **Entorno Local:** MySQL en MAMP o MySQL Server nativo (`127.0.0.1:3306`), base de datos `bd`.
2. **Entorno Nube:** Aiven MySQL Gestionado con conexión cifrada obligatoria TLS (`DB_SSL_CA`).

### 5.1 Catálogo de Tablas del Esquema

El esquema relacional consta de **22 tablas normalizadas**:

```mermaid
erDiagram
    tusuarios ||--o{ tventas : "registra"
    tusuarios ||--o{ tcortescaja : "ejecuta"
    tusuarios ||--o{ tauditoria : "genera"
    tclientes ||--o{ tventas : "compra"
    testadosventa ||--o{ tventas : "clasifica"
    tmetodospago ||--o{ tventas : "paga con"
    tventas ||--|{ tdetalleventas : "contiene"
    tproductos ||--o{ tdetalleventas : "forma"
    tcategorias ||--o{ tproductos : "agrupa"
    tproductos ||--o{ tproductos_variantes : "tiene"
    ttamanos ||--o{ tproductos_variantes : "define"
    tproductos ||--o{ tmovimientosinventario : "registra"
```

| Tabla | Propósito y Columnas Principales |
|---|---|
| `tusuarios` | Cuentas de acceso al sistema (`id`, `nombre`, `email`, `password_hash`, `rol_id`, `activo`, `ultimo_login`). |
| `troles` | Catálogo de perfiles autorizados (`id`, `nombre`: `Administrador`, `Vendedor`). |
| `tclientes` | Directorio de clientes (`id`, `nombre`, `telefono`, `email`). |
| `tcategorias` | Categorías comerciales del menú (`id`, `nombre`, `descripcion`, `activo`). |
| `tproductos` | Catálogo maestro de productos (`id`, `nombre`, `categoria_id`, `precio_base`, `stock`, `stock_minimo`, `stock_maximo`, `imagen_url`, `activo`). |
| `ttamanos` | Variantes de porción/tamaño (`id`, `nombre`: Chico, Mediano, Grande). |
| `tproductos_variantes` | Precios específicos por tamaño (`id`, `producto_id`, `tamano_id`, `precio`). |
| `tventas` | Registro inmutable de transacciones (`id`, `codigo_venta`, `cliente_id`, `usuario_id`, `total`, `metodo_pago_id`, `estado_id`, `servicio`, `mesa`, `fecha_venta`). |
| `tdetalleventas` | Renglones de la orden (`id`, `venta_id`, `producto_id`, `variante_id`, `cantidad`, `precio_unitario`, `subtotal`). |
| `testadosventa` | Estados de la orden (`id`, `nombre`: Pendiente, En preparación, Entregado, Cancelado). |
| `tmetodospago` | Formas de liquidación (`id`, `nombre`: Efectivo, Tarjeta, Transferencia). |
| `tpagos` | Detalles del pago monetario (`id`, `venta_id`, `monto_recibido`, `cambio`, `referencia`). |
| `tcortescaja` | Arqueos de caja continuos (`id`, `usuario_id`, `fecha_hora_inicio`, `fecha_hora_cierre`, `total_efectivo`, `total_tarjeta`, `total_transferencia`, `total_general`, `fecha_registro`). |
| `tauditoria` | Bitácora de trazabilidad obligatoria (`id`, `usuario_id`, `accion`, `modulo`, `detalles`, `ip_origen`, `fecha`). |
| `tmovimientosinventario` | Kardex de inventario (`id`, `producto_id`, `tipo_movimiento_id`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `fecha`). |
| `ttiposmovimiento` | Tipos de ajuste (`id`, `nombre`: Entrada, Salida, Ajuste Manual, Venta). |
| `tdevoluciones` | Reclamaciones y cancelaciones monetarias (`id`, `venta_id`, `tipo_id`, `estado_id`, `motivo`). |
| `testadosdevolucion` | Estados de devolución (`id`, `nombre`). |
| `ttiposdevolucion` | Catálogo de tipos de devolución (`id`, `nombre`). |
| `tcodigosrecuperacion` | Tokens temporales de reseteo de contraseña (`id`, `usuario_id`, `codigo_hash`, `expira_en`, `usado`). |
| `tvalidacion_usuarios` | Tokens de validación inicial de correo electrónico (`id`, `usuario_id`, `codigo`, `expiracion`). |
| `tschema_migrations` | Control de versión del esquema SQL (`version`, `applied_at`). |

### 5.2 Sistema de Migraciones Versionadas

Cualquier cambio a la estructura de la base de datos debe empaquetarse en un script SQL dentro de `database/migraciones/` siguiendo la nomenclatura `XXX_descripcion.sql`.

Para aplicar las migraciones pendientes:
```bash
python scripts/apply_migrations.py
```
El script verifica la tabla `tschema_migrations`, aplica los archivos ordenados en una transacción y registra su ejecución exitosa.

---

## 6. Pool de Conexiones (`bd.py`)

Para maximizar el rendimiento y evitar la sobrecarga de apertura y cierre constante de conexiones TCP/TLS, la aplicación implementa `PooledDB` de **DBUtils**.

### 6.1 Características del Pool
- **Parámetros:**
  - `maxconnections=10`: Límite seguro para bases de datos compartidas.
  - `mincached`: En entorno local inicializa 2 conexiones en reposo para máxima velocidad; en Aiven (`NUBE`) inicia en 0 para evitar retardos SSL durante el arranque.
  - `ping=4`: Comprueba la salud de la conexión antes de entregarla mediante `ping()`, reconectando automáticamente si el socket expiró.
  - `cursorclass=pymysql.cursors.DictCursor`: Retorna registros como diccionarios de Python (`columna: valor`).
- **Cifrado TLS:** Si `APP_ENV=NUBE`, valida la existencia del certificado CA y activa `ssl_verify_cert=True` y `ssl_verify_identity=True`.

### 6.2 Uso Recomendado en Controladores
```python
from bd import Obtener_Conexion

def mi_consulta_segura(producto_id):
    conn = Obtener_Conexion()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, nombre, stock FROM tproductos WHERE id = %s AND activo = 1;"
            cursor.execute(sql, (producto_id,))
            return cursor.fetchone()
    finally:
        conn.close()  # Devuelve la conexión al pool (no destruye el socket)
```

---

## 7. Seguridad, Autenticación y Autorización

### 7.1 Decoradores de Acceso (`utils.py`)

- **`@login_required`**: Valida que la clave `'usuario_id'` resida en la sesión activa de Flask. Si la sesión no existe, redirige al usuario a la vista de login preservando la URL solicitada.
- **`@admin_required`**: Valida que el rol del usuario autenticado corresponda a `'Administrador'`. Si un usuario con rol `'Vendedor'` intenta consumir un endpoint protegido, se aborta la petición con código HTTP **403 Forbidden**.
- **Revalidación Periódica de Sesión:** Si transcurren más de `SESSION_VALIDATION_INTERVAL_SECONDS` (def. 60s), el sistema verifica en segundo plano que el usuario siga existiendo y permanezca activo en `tusuarios`.

### 7.2 Protección contra Ataques Comunes

1. **Inyección SQL (SQLi):**
   - **Regla Estricta:** 100% de consultas parametrizadas mediante tuplas `%s`. Prohibida la interpolación de cadenas `f"..."` o `format()`.
2. **Cross-Site Request Forgery (CSRF):**
   - Protegido mediante `Flask-WTF`. Formularios y llamadas AJAX POST/PUT/DELETE deben incluir el token CSRF en encabezado `X-CSRFToken` o campo oculto `csrf_token`.
3. **Fuerza Bruta y DoS:**
   - Protegido mediante `Flask-Limiter` en rutas críticas (ej. máximo 5 intentos por minuto en `/login` y `/recuperar-contrasena`).
4. **Fuga de Hashes de Contraseñas:**
   - Prohibido el uso de `SELECT *` o `SELECT u.*` en tablas de usuarios.

---

## 8. Catálogo de Blueprints y Rutas API

### 8.1 Autenticación (`autenticacion_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET`, `POST` | `/` | Pública | Pantalla de inicio de sesión y autenticación de credenciales |
| `GET` | `/salir` | Login | Cierra la sesión activa y limpia variables de sesión |
| `GET`, `POST` | `/recuperar-contrasena` | Pública | Solicita código de recuperación por correo electrónico |
| `GET`, `POST` | `/verificar-codigo` | Pública | Valida token de 6 dígitos enviado por correo |
| `GET`, `POST` | `/actualizar-contrasena` | Pública | Asigna la nueva contraseña al usuario validado |

### 8.2 Ventas y POS (`ventas_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET` | `/menu` | Login | Vista del Punto de Venta con filtro de categorías y carrito |
| `GET` | `/ordenes` | Login | Monitor de pedidos en tiempo real |
| `GET` | `/api/ordenes` | Login | Retorna listado JSON de pedidos activos |
| `GET` | `/api/ordenes/<id>/detalles` | Login | Retorna el desglose de productos de un pedido |
| `POST` | `/api/ordenes/<id>/estado` | Login | Actualiza estado de pedido (o cancela con motivo obligatorio) |
| `GET` | `/historial` | Login | Vista del historial de ventas con filtros de fecha |
| `GET` | `/api/historial-ventas` | Login | Endpoint paginado seguro (`por_pagina` acotado 1-100) |
| `GET` | `/api/historial-ventas/<id>` | Login | Detalle de renglones de una venta registrada |
| `POST` | `/api/ventas/crear` | Login | Registra una nueva transacción y descuenta inventario |
| `GET` | `/api/historial-ventas/exportar` | Login | Descarga el reporte filtrado en formato CSV/Excel con BOM UTF-8 |

### 8.3 Finanzas y Caja (`finanzas_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET` | `/corteCaja` | Admin | Interfaz de corte de caja (`fechaDesde` readonly sugerida) |
| `POST` | `/filtrarVentas` | Admin | Consulta ventas agrupadas por método de pago para el corte |
| `GET` | `/api/corteCaja/ultimo` | Admin | Retorna timestamp de cierre del último corte registrado |
| `GET` | `/api/corteCaja/<id>` | Admin | Retorna los detalles de un corte específico |
| `POST` | `/guardarCorteCaja` | Admin | Registra corte continuo verificando ausencia de huecos |
| `GET` | `/reporteFinanciero` | Admin | Vista del histórico de cortes y métricas de recaudación |
| `GET` | `/api/cortes/exportar-excel` | Admin | Exportación de cortes financieros en formato CSV/Excel |

### 8.4 Inventario (`inventario_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET` | `/inventario` | Admin | Tabla de existencias con alertas de stock mínimo |
| `POST` | `/api/inventario/actualizar` | Admin | Modifica stock o límites requiriendo motivo obligatorio |

### 8.5 Catálogo de Productos (`productos_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET` | `/gestionProductos` | Admin | Vista de administración del catálogo y dropzone de imagen |
| `GET` | `/api/categorias` | Admin | Listado JSON de categorías activas |
| `GET` | `/api/tamanos` | Admin | Listado de tamaños disponibles |
| `POST` | `/api/productos/guardar` | Admin | Alta o edición de producto con carga de imagen |
| `POST` | `/api/productos/eliminar` | Admin | Desactivación lógica de un producto del catálogo |
| `GET` | `/api/productos/<id>` | Admin | Consulta de ficha técnica de un producto |

### 8.6 Gestión de Usuarios (`usuarios_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET` | `/gestionUsuarios` | Admin | Panel de altas, bajas y permisos de personal |
| `POST` | `/api/usuarios/guardar` | Admin | Alta o modificación de usuario y contraseña |
| `GET` | `/api/usuarios/<id>` | Admin | Consulta datos de un usuario por ID |
| `POST` | `/gestionUsuarios/eliminar/<id>` | Admin | Desactiva a un usuario |
| `POST` | `/gestionUsuarios/activar/<id>` | Admin | Reactiva a un usuario previamente deshabilitado |

### 8.7 Rutas Generales y Core (`generales_bp.py` - Prefijo: `/`)

| Método | Ruta | Auth | Descripción |
|---|---|:---:|---|
| `GET` | `/bienvenida` | Login | Dashboard de bienvenida y accesos rápidos |
| `GET` | `/health` | Pública | Healthcheck del servicio y conexión a BD |
| `POST` | `/api/guardar-pdf` | Login | Almacena comprobantes de tickets silenciosamente en servidor |
| `GET` | `/api/pdfs/<tipo>/<nombre>` | Login | Descarga segura de comprobantes almacenados |

---

## 9. Suite de Pruebas Automatizadas (pytest)

El proyecto cuenta con una robusta suite de pruebas unitarias y de integración que valida el comportamiento de los endpoints, las reglas contables y los filtros de seguridad sin requerir una conexión activa a la base de datos real.

### 9.1 Ejecución de las Pruebas

Para correr la suite completa:
```bash
.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Para ejecutar con reporte detallado:
```bash
.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider
```

Para probar un módulo específico:
```bash
.venv\Scripts\python.exe -m pytest tests/test_ventas.py -v
```

### 9.2 Métricas de la Suite
- **Total de pruebas:** 328
- **Pruebas superadas:** 323
- **Pruebas omitidas (skipped):** 5 *(Pruebas reservadas estrictamente para integración con base de datos real activa)*
- **Fallos:** 0

### 9.3 Análisis Estático de Código (Linter)
El código debe cumplir con las directrices de formato PEP8 y buenas prácticas mediante **Ruff**:
```bash
.venv\Scripts\ruff.exe check .
```

---

## 10. Gestión y Almacenamiento de Archivos

| Tipo de Archivo | Ruta en Disco | ¿En Git? | Controlador Responsable |
|---|---|:---:|---|
| **Tickets de Venta (PDF)** | `instance/pdfs/tickets_ventas/` | ❌ No | `/api/guardar-pdf` (Generales BP) |
| **Cortes de Caja (PDF)** | `instance/pdfs/cortes_de_caja/` | ❌ No | Generado por jsPDF en cliente |
| **Imágenes de Productos** | `static/images/productos/` | ✅ Sí | `/api/productos/guardar` (Productos BP) |
| **Exportaciones Excel/CSV** | Dinámico en memoria (`io.BytesIO`) | ❌ No | `/api/historial-ventas/exportar` y `/api/cortes/exportar-excel` |

> [!NOTE]
> La carpeta `instance/` es creada automáticamente durante la inicialización de la aplicación (`app.py`) y permanece protegida fuera del repositorio.

---

## 11. Despliegue en Producción y Nube (Aiven)

Para desplegar la aplicación en un servidor productivo con base de datos gestionada en Aiven:

### Paso 1: Configurar Variables de Producción en `bd.env`
```ini
APP_ENV=NUBE
FLASK_DEBUG=False
SECRET_KEY=clave-robusta-generada-con-openssl-rand-hex-32
TRUST_PROXY=True
RATELIMIT_STORAGE_URI=redis://default:password@redis-server:6379/0

DB_HOST=mysql-servidor-aiven.aivencloud.com
DB_PORT=15234
DB_USER=avnadmin
DB_PASSWORD=contrasena_secreta_aiven
DB_NAME=defaultdb
DB_SSL_CA=/etc/ssl/certs/aiven-ca.pem
```

### Paso 2: Servidor WSGI Productivo (Waitress o Gunicorn)
En entornos de producción no debe usarse el servidor de desarrollo `app.run()`.

En **Windows Server** (usando Waitress):
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 --threads=8 app:create_app()
```

En **Linux Server** (usando Gunicorn detrás de Nginx):
```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
```

### Paso 3: Aplicar Migraciones en Nube
> [!IMPORTANT]
> Realizar un respaldo completo antes de migrar. Aplicar las migraciones con:
```bash
python scripts/apply_migrations.py
```

---

## 12. Control de Versiones y Flujo Git

El repositorio se rige bajo la convención de **Commits Semánticos**:

| Prefijo | Significado | Ejemplo |
|---|---|---|
| `feat:` | Nueva funcionalidad | `feat: agregar exportacion a excel en historial de ventas` |
| `fix:` | Corrección de error | `fix: evitar salto de fecha en corte de caja continuo` |
| `refactor:` | Modificación interna sin alterar funcionalidad | `refactor: modularizar funciones de calculo en finanzas` |
| `docs:` | Actualización de documentación | `docs: redactar manual de usuario y manual tecnico` |
| `test:` | Adición o ajuste de pruebas unitarias | `test: agregar pruebas para validacion de limites de paginacion` |
| `chore:` | Tareas de configuración, dependencias o tooling | `chore: actualizar requerimientos de desarrollo` |

**Rama activa de trabajo:** `feat/mejoras-operativas-pos`

---

## 13. Directrices para Agentes de IA (`AGENTS.md`)

Cualquier agente de inteligencia artificial que colabore en el proyecto debe acatar las reglas no negociables consagradas en `AGENTS.md`:

1. **Inmutabilidad de Ventas:** Prohibido implementar sentencias `DELETE` o `TRUNCATE` sobre `tventas` y `tdetalleventas`.
2. **Corte Continuo:** El campo `fechaDesde` en los cortes de caja debe basarse siempre en `SELECT MAX(fecha_hora_cierre) FROM tcortescaja`. Prohibido permitir huecos temporales.
3. **Auditoría Obligatoria:** Todo ajuste manual de inventario o cancelación de pedidos debe exigir un motivo y registrarse en `tauditoria`.
4. **Consultas Parametrizadas:** Cero tolerancia a concatenación de cadenas en SQL.

---

## 14. Guía de Solución de Problemas (Troubleshooting)

### 🔴 Error: `Can't connect to MySQL server on '127.0.0.1'`
- **Causa:** El motor de base de datos local (MAMP / MySQL) no está ejecutándose o está en un puerto distinto al `3306`.
- **Solución:** Iniciar los servidores en el panel de MAMP y verificar que `DB_PORT=3306` en `bd.env`.

### 🔴 Error: `DB_SSL_CA no apunta a un certificado CA existente`
- **Causa:** Se configuró `APP_ENV=NUBE`, pero la ruta del archivo `.pem` en `DB_SSL_CA` es errónea o inaccesible.
- **Solución:** Validar la ruta absoluta del archivo y verificar permisos de lectura.

### 🔴 Error: `CSRF token missing or incorrect` (HTTP 400)
- **Causa:** Una llamada AJAX mediante `fetch` o un formulario POST no incluyó el encabezado `X-CSRFToken`.
- **Solución:** Asegurar que la petición incluya el valor del input `#csrf_token` generado por Jinja2.

### 🔴 Fallo en Pytest: `MySQL connection refused`
- **Causa:** Una prueba unitaria intentó conectarse a la base de datos real en lugar de usar mocks.
- **Solución:** Emplear `monkeypatch` en el test para simular el retorno de `Obtener_Conexion()` o de los helpers del modelo.

---

*📄 Documento de referencia técnica del sistema Coffee Hacienda POS.*  
*☕ Coffee Hacienda — Haciendas de San Vicente, 63737 San Vicente, Nay.*

