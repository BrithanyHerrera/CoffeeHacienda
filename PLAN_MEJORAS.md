# Plan de mejoras — Coffee Hacienda

## Objetivo

Convertir el proyecto actual en un punto de venta seguro, consistente y mantenible, usando:

- **MySQL local** para desarrollo y pruebas.
- **Aiven MySQL** para el entorno en la nube.
- Un único esquema versionado mediante migraciones, para evitar que ambas bases se separen.

> Regla principal: ningún cambio de esquema se hará manualmente primero en Aiven. Se crea como migración, se prueba en local, se respalda Aiven y después se aplica en la nube.

## Estado general

La rama `main` cubre los controles críticos que dependen del código. La base
local MAMP/MySQL 5.7.24 respondió correctamente, tiene las migraciones 2 y 3, y
las pantallas principales pasaron una prueba de humo de solo lectura. El 30 de
agosto de 2026 se creó y validó un respaldo manual de Aiven y se aplicaron allí
las migraciones 002 y 003 mediante una conexión TLS verificada. Siguen
requiriendo intervención humana la rotación de secretos, la creación de una
cuenta web de mínimo privilegio y una prueba de restauración separada. Las
pruebas que escriben datos se mantienen aisladas para no alterar las bases de
uso normal.

**Leyenda:** `[x]` completado · `[~]` parcial · `[ ]` pendiente.

## Ruta de trabajo

| Fase | Prioridad | Resultado esperado |
|---|---:|---|
| 0. Contención | P0 | Cerrar accesos críticos y retirar datos sensibles |
| 1. Ventas e inventario | P0 | Importes confiables, cancelaciones auditables y stock consistente |
| 2. Base de datos local/Aiven | P0–P1 | Un solo esquema reproducible mediante migraciones |
| 3. Seguridad web | P1 | Permisos, CSRF, sesiones, XSS y archivos protegidos |
| 4. Pruebas y calidad | P1–P2 | Cambios verificables automáticamente |
| 5. Operación en nube | P2 | Despliegue, respaldos, logs y monitoreo básicos |

---

## Fase 0 — Contención inmediata

### 0.1 Reparar la recuperación de contraseña

- [x] No permitir `/actualizar-contrasena` solo por tener un correo en sesión.
- [x] Al validar el código, guardar en sesión un estado de verificación de un solo uso y con expiración corta.
- [x] Consumir el código y el permiso temporal dentro de la misma operación que cambia la contraseña.
- [x] Usar `secrets` en lugar de `random` para generar códigos.
- [x] Limitar intentos de verificación y actualización.
- [x] Invalidar las sesiones del usuario mediante `sesion_version` después del cambio.

**Criterio de aceptación:** visitar directamente la ruta final, reutilizar un código o usar un código expirado nunca permite cambiar una contraseña.

### 0.2 Retirar credenciales y datos personales del repositorio

- [x] Sustituir los datos reales de `bd.sql` por datos ficticios o eliminar completamente los `INSERT` sensibles.
- [x] Crear el administrador local mediante un script que genera el hash sin guardar la contraseña.
- [~] Las contraseñas de las 5 cuentas activas conservadas en Aiven no se
  rotarán por decisión del propietario; las 4 cuentas inactivas permanecen
  bloqueadas. Se conserva este punto como riesgo aceptado, no como fallo técnico.
- [~] Rotar las credenciales que hayan estado en versiones anteriores de
  `bd.env`: `avnadmin`, el usuario web de Aiven y `SECRET_KEY` ya se renovaron;
  `MAIL_PASSWORD` se conserva por decisión del propietario.
- [x] Limpiar esos archivos del historial Git si el repositorio se compartió o subió a un remoto.
- [x] Crear `bd.env.example` únicamente con nombres de variables y valores ficticios.

**Criterio de aceptación:** una búsqueda en el historial y en la rama actual no encuentra correos reales, contraseñas ni secretos utilizables.

### 0.3 Dejar de exponer contraseñas o hashes

- [x] Cambiar las consultas de usuario para seleccionar columnas explícitas; nunca `u.*`.
- [x] No incluir `contrasena` en ninguna respuesta JSON.
- [x] Eliminar de la interfaz la opción de mostrar el hash.
- [x] Exigir rol Administrador para consultar información individual de otros usuarios.

**Criterio de aceptación:** ninguna respuesta HTTP ni elemento del navegador contiene el hash de contraseña.

### 0.4 Configuración segura por defecto

- [x] Eliminar `debug=True` como valor fijo.
- [x] Definir configuraciones separadas: `DevelopmentConfig`, `TestingConfig` y `ProductionConfig`.
- [x] En producción activar cookies `Secure`, `HttpOnly` y `SameSite=Lax` o más restrictivo.
- [x] No devolver `str(e)` al navegador; registrar el detalle y usar mensajes genéricos.

---

## Fase 1 — Integridad de ventas, caja e inventario

### 1.1 El servidor es la única autoridad de precios

El navegador debe enviar únicamente:

- Identificador de producto o variante.
- Cantidad.
- Cliente, mesa y método de pago.
- Dinero recibido cuando corresponda.

El servidor debe:

1. Consultar productos, variantes y precios vigentes.
2. Validar cantidades positivas.
3. Calcular subtotales, total y cambio usando `Decimal`.
4. Validar el método de pago contra la base de datos.
5. Guardar cabecera, detalles y descuento de stock en una sola transacción.

**Criterio de aceptación:** modificar precio o total desde las herramientas del navegador no altera el importe registrado.

### 1.2 Corregir métodos de pago

- [x] Decidir el catálogo definitivo: Efectivo, Tarjeta y Transferencia.
- [x] Dejar de depender de IDs escritos directamente en JavaScript.
- [x] Consultar el catálogo en el servidor y usar claves estables como `EFECTIVO`, `TARJETA` y `TRANSFERENCIA`.
- [x] Actualizar reportes y cortes para usar los tres métodos acordados.

**Criterio de aceptación:** cada venta aparece bajo el mismo método en menú, historial, base de datos y corte.

### 1.3 Registrar correctamente tamaños y variantes

- [x] Agregar `variante_id` al detalle de venta cuando aplique.
- [x] Conservar instantáneas independientes de nombre, tamaño y precio vendido.
- [x] No reconstruir ventas antiguas uniendo todas las variantes actuales del producto.

**Criterio de aceptación:** cambiar el catálogo después de una venta no modifica lo que muestra su ticket o historial.

### 1.4 Cancelaciones auditables

- [x] No borrar físicamente ventas canceladas.
- [x] Cambiar su estado a `Cancelado`.
- [x] Reponer stock y registrar el movimiento dentro de la misma transacción.
- [x] Guardar usuario, fecha y motivo de cancelación.
- [x] Evitar una segunda cancelación o reposición duplicada.

**Criterio de aceptación:** la venta sigue en el historial, el stock se repone exactamente una vez y existe trazabilidad.

### 1.5 Cortes de caja confiables

- [x] Recalcular totales en el servidor consultando ventas completadas del rango.
- [x] Excluir pendientes, canceladas y reembolsadas según la regla de negocio.
- [x] No aceptar del navegador los totales calculados como fuente de verdad.
- [x] Validar rangos, impedir solapamientos o duplicados y registrar quién cerró la caja.
- [x] Guardar dinero con `DECIMAL`, no `float` ni `varchar`.

### 1.6 Inventario atómico

- [x] Hacer el cambio de stock y su movimiento en una sola transacción.
- [x] Convertir `tmovimientosinventario.Id` en `AUTO_INCREMENT`; eliminar `MAX(Id)+1`.
- [x] Descontar con una operación condicional, comprobando stock suficiente en el mismo `UPDATE`.
- [x] Registrar movimientos de ventas, cancelaciones y ajustes manuales.

---

## Fase 2 — MySQL local y Aiven sin divergencias

### 2.1 Papeles de cada entorno

| Entorno | Uso | Datos permitidos |
|---|---|---|
| Local | Desarrollo, migraciones y pruebas manuales | Datos ficticios o anonimizados |
| Aiven | Nube/producción | Datos reales, acceso restringido y respaldos |
| Testing | Pruebas automáticas | Base temporal creada y destruida por la suite |

No se debe usar Aiven para experimentar con cambios de esquema.

### 2.2 Migraciones

- [x] Incorporar migraciones SQL numeradas.
- [x] Mantener `bd.sql` como esquema inicial reproducible y saneado, sin datos operativos personales.
- [~] La migración actual es repetible; falta una reversión formal cuando sea posible.
- [x] Registrar en `tschema_migrations` qué versión de esquema está aplicada.

Flujo obligatorio:

1. Crear la migración.
2. Aplicarla en una base local limpia.
3. Cargar datos ficticios.
4. Ejecutar pruebas.
5. Probar actualización desde una copia del esquema anterior.
6. Crear respaldo de Aiven.
7. Aplicar la migración en Aiven.
8. Ejecutar una prueba de humo y verificar logs.

### 2.3 Configuración

- [x] Mantener una sola interfaz `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME` para ambos entornos.
- [x] Elegir el entorno con `APP_ENV`, sin duplicar lógica por toda la aplicación.
- [x] Construir rutas a `bd.env`, imágenes y PDFs a partir de la raíz de la aplicación.
- [x] En Aiven verificar TLS con el certificado CA suministrado por el servicio.
- [x] Aplicar mínimo privilegio a la cuenta web: `coffee_hacienda_app` sólo
  conserva `SELECT`, `INSERT`, `UPDATE` y `DELETE` sobre la base de la
  aplicación, sin permisos globales, de esquema ni administración.

### 2.4 Respaldos y restauración

- [x] Confirmar que los respaldos automáticos de Aiven están activos.
- [x] Crear y validar un respaldo manual antes de aplicar las migraciones 002/003.
- [x] Conservar el respaldo real fuera del repositorio, en
  `C:\CoffeeHacienda_Backups\aiven_antes_migraciones_20260830_225048.sql`.
- [x] Verificar la integridad básica del respaldo: 20 tablas, datos de 16 tablas,
  marcador de finalización y SHA-256
  `0D69F320E717472190BCDF7D94D29DF3A7C1DD7F4ECF7F0E708B98D42762CE05`.
- [ ] Probar periódicamente una restauración en una instancia o base separada.
- [x] Nunca guardar respaldos con datos reales dentro del repositorio.

---

## Fase 3 — Seguridad web

- [x] Mantener CSRF habilitado en operaciones de escritura y enviar el token desde `fetch`.
- [x] Definir y aplicar permisos en el servidor.
- [x] Exigir Administrador para usuarios, productos, inventario, cortes y reportes sensibles.
- [~] Escapar interpolaciones dinámicas; quedan estructuras heredadas con `innerHTML` por modularizar.
- [x] Validar longitud y formato de datos principales en el servidor.
- [x] Restringir PDFs a extensión `.pdf`, firma `%PDF-`, tamaño máximo y nombre generado por el servidor.
- [x] Guardar documentos fuera de `/static` y entregarlos mediante una ruta autenticada.
- [x] Generar nombres únicos para evitar sobrescrituras.
- [x] Definir `MAX_CONTENT_LENGTH` para PDFs e imágenes.
- [x] Agregar encabezados CSP, HSTS en HTTPS, `X-Content-Type-Options` y protección contra marcos.
- [~] Soportar almacenamiento compartido con `RATELIMIT_STORAGE_URI`; falta proporcionar Redis en el despliegue.

---

## Fase 4 — Pruebas y mantenibilidad

### 4.1 Base técnica

- [x] Convertir `app.py` a un patrón de fábrica `create_app(config)`.
- [~] Separar lógica de negocio de las rutas y del acceso SQL.
- [x] Bloquear versiones de dependencias y documentar Python 3.12.
- [x] Añadir Ruff para análisis estático crítico.
- [x] Dividir los JavaScript grandes en módulos y eliminar funciones duplicadas.

### 4.2 Pruebas mínimas obligatorias

1. [x] La recuperación prueba expiración de sesión/código, reutilización y límite de cinco intentos.
2. [x] Un empleado no puede consultar hashes ni ejecutar acciones administrativas.
3. [x] Manipular precios o totales del cliente no afecta una venta.
4. [x] Dos ventas concurrentes se prueban en MySQL aislado y nunca dejan stock negativo.
5. [x] Cancelar repone stock una sola vez, conserva la venta y genera auditoría.
6. [x] El flujo catálogo, venta, inventario, cancelación y corte se prueba contra MySQL aislado.
7. [x] El historial conserva nombre, tamaño y precio después de cambiar el catálogo.
8. [x] Añadir una prueba de navegador que confirme que HTML se muestra como texto.
9. [x] PDFs e imágenes validan firma, límite de tamaño y nombres generados dentro de sus carpetas.
10. [x] Las migraciones 002 y 003 están aplicadas y verificadas tanto en local como en Aiven.

### 4.3 Integración continua

La aplicación se opera localmente. Para cada cambio debe ejecutarse:

- [x] Análisis estático crítico de Python mediante Ruff.
- [x] Suite local: 284 pruebas correctas y 100% de cobertura exclusiva del
  código de producción (2,149 líneas, ninguna sin cubrir).
- [x] Las dos pruebas de lectura MySQL pasan contra la base local usando `RUN_DB_TESTS=1`.
- [x] Cinco pruebas integrales, incluida concurrencia, pasan en una base MySQL temporal creada y eliminada automáticamente.
- [x] La prueba concurrente confirma una sola venta, un solo movimiento y stock final no negativo.
- [x] El esquema inicial y las migraciones 002/003 se validaron desde cero contra MySQL 8.4.
- [x] GitHub Actions ejecuta Ruff y rechaza la suite local si la cobertura de producción baja de 100%; MySQL aislado permanece como validación local deliberada.
- [~] Búsqueda de secretos actuales realizada; falta revisar el historial y automatizar dependencias vulnerables.

### 4.4 Cobertura por módulos — cierre al 100%

La medición ya excluye `tests/` y `scripts/`; por tanto, el porcentaje representa
solamente la aplicación que se ejecuta en uso normal. El corte global terminó
con **284 pruebas correctas, 5 pruebas MySQL aisladas separadas y 100% de
cobertura del código de producción: 2,149 líneas y ninguna sin cubrir**.

#### Módulos ya validados al 100%

| Grupo | Módulos | Estado |
|---|---|---|
| Núcleo de la aplicación | `app.py`, `bd.py`, `config.py`, `extensions.py`, `utils.py` | [x] 100% |
| Productos y catálogo | `modelsProductos.py`, `modelsProductosMenu.py` | [x] 100% |
| Usuarios y acceso a datos | `modelsUsuarios.py`, `modelsLogin.py` | [x] 100% |
| Ventas | `modelsVentas.py` | [x] 100% |
| Inventario | `modelsInventario.py` | [x] 100% |
| Caja | `modelsCorteCaja.py` | [x] 100% |
| Recuperación de contraseña | `modelsRecuperacion.py` | [x] 100% |
| Historial y limpieza | `modelsHistorial.py`, `modelsLimpieza.py` | [x] 100% |
| Rutas de autenticación y recuperación | `autenticacion_bp.py` | [x] 100% |
| Rutas de finanzas y cortes | `finanzas_bp.py` | [x] 100% |
| Rutas generales y archivos | `generales_bp.py` | [x] 100% |
| Rutas de inventario | `inventario_bp.py` | [x] 100% |
| Rutas de productos | `productos_bp.py` | [x] 100% |
| Rutas de usuarios | `usuarios_bp.py` | [x] 100% |
| Rutas de ventas e historial | `ventas_bp.py` | [x] 100% |

- [x] Configurar una métrica real que mida únicamente código de producción.
- [x] Llevar el núcleo y todos los modelos de acceso a datos al 100%.
- [x] Terminar las pruebas de las siete áreas de rutas indicadas en la tabla.
- [x] Ejecutar nuevamente la suite completa y corregir cualquier fallo detectado.
- [x] Activar en la validación automática el requisito estricto de 100%.
- [x] Confirmar Ruff y MySQL aislado, registrar el cierre y hacer `push`.

---

## Fase 5 — Operación en Aiven

- [x] Documentar Waitress detrás de un proxy HTTPS y soporte seguro de `ProxyFix`.
- Mantener imágenes y PDFs en almacenamiento persistente u objetos, no en el disco efímero de una instancia web.
- Configurar logs estructurados sin contraseñas, códigos ni datos financieros sensibles.
- [~] Registrar eventos de auditoría; cancelaciones, ventas y ajustes ya generan trazabilidad.
- [x] Añadir un endpoint de salud que compruebe aplicación y conectividad básica sin revelar datos internos.
- Monitorear errores, latencia, conexiones ocupadas y espacio de almacenamiento.
- [x] Definir un procedimiento de reversión para aplicación y migraciones.

---

## Primer bloque recomendado

Antes de agregar nuevas funciones, completar en este orden:

- [x] Corregir recuperación de contraseña.
- [~] Rotar secretos y retirar datos reales del repositorio e historial (historial purgado, pendiente rotación manual).
- [x] Eliminar exposición de contraseñas/hashes.
- [x] Recalcular precios y total de venta en el servidor.
- [x] Corregir el catálogo de métodos de pago y eliminar IDs fijos del JavaScript.
- [x] Cancelar sin borrar, reponer inventario y guardar auditoría atómicamente.
- [x] Introducir una migración SQL para local y Aiven.
- [x] Añadir pruebas automatizadas y exigir 100% de cobertura del código de producción.

El bloque de código crítico está cerrado. Aiven ya cuenta con el respaldo previo
y las migraciones 002/003. Antes de usarlo activamente todavía deben rotarse los
secretos expuestos históricamente y configurarse una cuenta web de mínimo
privilegio.

---

## Cierre de la versión estable local — actualizado el 30 de agosto de 2026

- [x] Cambios de la versión estable integrados en `main`.
- [x] Ventas, cancelaciones, inventario, caja, sesiones y recuperación reforzados.
- [x] Esquema saneado y migraciones 002/003 preparadas y verificadas en una base limpia.
- [x] Corregir las rutas rotas posteriores a la conversión a blueprints: login, permisos, salida y PDF de corte.
- [x] Corregir y validar el arranque mediante la fábrica de aplicación con Waitress.
- [x] Cargar `SECRET_KEY` después de leer `bd.env` y fallar con un mensaje claro si no está configurada.
- [x] Permitir que el servidor inicie y muestre el login aunque MySQL esté temporalmente fuera de servicio.
- [x] Validación local ampliada: 284 pruebas correctas, 2,149 líneas de
  producción medidas y 100% de cobertura real; la validación automática ya
  impide que el porcentaje disminuya.
- [x] Validación MySQL aislada: 5 pruebas correctas para esquema, venta, concurrencia, inventario, cancelación, corte y snapshots históricos.
- [x] La conexión local, `/health` y 11 rutas principales responden correctamente con MAMP activo.
- [x] Archivo `bd.env` y credenciales reales excluidos de Git.
- [x] Aplicar las migraciones en la base local real después de crear un respaldo.
- [x] Crear y validar un respaldo manual de Aiven fuera del repositorio.
- [x] Aplicar las migraciones 002 y 003 en Aiven y comprobar sus 10 columnas,
  5 índices, 4 relaciones y el `AUTO_INCREMENT` de movimientos de inventario.
- [x] Rotar `avnadmin`, crear credenciales nuevas para la aplicación y renovar
  `SECRET_KEY`; las comprobaciones de salud local y Aiven respondieron HTTP 200.
- [~] Conservar temporalmente `MAIL_PASSWORD` por decisión del propietario; debe
  rotarse si esa contraseña de aplicación de Gmail llegó a compartirse.
- [x] Crear y validar `coffee_hacienda_app` con permisos mínimos en Aiven.
- [~] Conservar las contraseñas de las 5 cuentas activas por decisión del
  propietario; las 4 cuentas inactivas siguen bloqueadas.
- [ ] Probar la restauración del respaldo en una base o servicio separado.
- [x] Integrar la rama a `main` después de una prueba manual del flujo de venta en el equipo local.
- [x] Validación final posterior a la rotación: Ruff sin errores, 284 pruebas
  locales y 5 pruebas MySQL aisladas correctas, con `/health` HTTP 200 tanto en
  local como en Aiven mediante la cuenta de mínimo privilegio.
