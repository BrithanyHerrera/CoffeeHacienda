# 🔍 Reporte de Análisis Exhaustivo y Plan de Trabajo — CoffeeHacienda (Flask)

> **Fecha de actualización:** 2026-10-28  
> Este documento está dividido en dos partes claramente diferenciadas:
> 1. **PARTE 1 (Arriba / Prioridad de Negocio): Requerimientos y Mejoras del Usuario** — Solicitudes de operación, UX y flujo del negocio (extraídas de capturas operativas de WhatsApp).
> 2. **PARTE 2: Hallazgos Técnicos y de Seguridad de la IA** — Auditoría estática de código, bugs funcionales y seguridad.

---

# 📌 PARTE 1 — Requerimientos y Mejoras del Usuario (WhatsApp / Operación)

Estos requerimientos representan las necesidades operativas, de negocio, interfaz y experiencia de usuario reportadas directamente por el desarrollador/propietario:

### 1. Corte de caja continuo obligatorio (Solo desde el último corte) — 🔴 P0
* **Origen:** Solicitud operativa del área de finanzas/caja.
* **Problema actual:** `fechaDesde` es un campo de fecha libre en `corteCaja.html`. El usuario puede seleccionar fechas arbitrarias, provocando huecos temporales sin auditar o solapamientos con cortes previos.
* **Requerimiento:** El corte más actual debe ser **únicamente realizable a partir de la fecha y hora de cierre del último corte registrado**.
* **Acciones técnicas:**
  - `fechaDesde` precargado automáticamente con `SELECT MAX(fecha_hora_cierre) FROM tcortescaja` y bloqueado como `readonly`.
  - `fechaHasta` precargado con la fecha y hora actual (`min = fechaDesde`).
  - Validación estricta en el servidor en `/guardarCorteCaja`.

---

### 2. Ciclo de vida y cancelación/expiración de pedidos pendientes — 🟠 P1
* **Origen:** Captura WhatsApp (*"Cancelar o Ver que hacer con los pedidos despues de cierto lapso de tiempo"*).
* **Problema actual:** Pedidos no cobrados o abandonados pueden permanecer indefinidamente como "Pendientes", reteniendo existencias de inventario o saturando el monitor de pedidos.
* **Solución técnica:**
  - Establecer una política de expiración o alerta visual por inactividad (ej. 30–60 minutos).
  - Implementar botón de cancelación con liberación automática de existencias.

---

### 3. Modales de confirmación con motivo para acciones críticas — 🟠 P1
* **Origen:** Captura WhatsApp (*"poner preguntas de confirmacion al hacer acciones como Ajustar stock , max , min etc"*).
* **Problema actual:** Modificaciones de inventario (`Ajustar stock`, `max`, `min`) y cancelaciones pueden ejecutarse por error o sin justificación.
* **Solución técnica:**
  - Modal estandarizado de confirmación que solicite obligatoriamente un *"Motivo"*.
  - El motivo se envía al backend y se almacena en la tabla `tauditoria` (campo `detalles`) para trazabilidad total.

---

### 4. Normalización de selección de mesas ("Para llevar" vs "Sin mesa") — 🟡 P2
* **Origen:** Captura WhatsApp (*"Especificar mesa: podemos dejar maybe 5 mesas y hacer que la seleccion de mesas sea en box; cuando sea para llevar no dejar sin mesa, dejar como 'Para llevar'"*).
* **Problema actual:** En el registro de ventas se muestra `"Sin mesa"` o texto libre desordenado como `"Mesa: 42"`.
* **Solución técnica:**
  - Reemplazar el campo de texto libre por un selector cerrado:
    1. Opción por defecto: `"Para llevar"`.
    2. Opciones de comedor: `"Mesa 1"` a `"Mesa 5"` o `"Barra"`.
  - Normalizar el valor en la base de datos y en los tickets generados.

---

### 5. Adaptabilidad y responsividad a pantalla dividida (Mitad de pantalla) — 🟡 P2
* **Origen:** Captura WhatsApp (*"Mejorar vistas en diff dimensiones (Mitad Pantalla)"*).
* **Problema actual:** En terminales POS donde se usa media pantalla (split screen con WhatsApp, música o terminal bancaria), las tablas y formularios se desbordan horizontalmente.
* **Solución técnica:**
  - Añadir media queries para pantallas medianas (`@media (max-width: 992px)`).
  - Envolver tablas en contenedores con `overflow-x: auto;` y usar `flex-wrap: wrap;` en toolbars.

---

### 6. Clasificación de catálogo y filtros simétricos — 🟢 P3
* **Origen:** Captura WhatsApp (*"Hacerlo por categorias"* y *"hacer simétrica esa area"*).
* **Problema actual:** Es difícil buscar productos rápidamente en mostrador, y los selectores de filtro de tamaños y categorías en el catálogo tienen márgenes y anchos asimétricos.
* **Solución técnica:**
  - Botones o pestañas de categorías en la vista de ventas.
  - Estructurar el contenedor de filtros con `display: flex; gap: 12px;` y asignar `flex: 1` a los inputs.

---

### 7. Modernización del botón de subida de imágenes — 🟢 P3
* **Origen:** Captura WhatsApp (*"Ver si se puede mejorar ese boton"* sobre `Seleccionar archivo`).
* **Problema actual:** El input nativo `<input type="file">` se muestra con el estilo gris por defecto del sistema operativo, desentonando con el diseño.
* **Solución técnica:**
  - Ocultar el input nativo y enlazar un `<label>` estilizado con botón personalizado, icono de cámara/subida y previsualización de imagen.

---

### 8. Almacenamiento seguro de tickets y exportación dinámica a Excel — 🟠 P1
* **Origen:** Captura WhatsApp (*"Guardar tickets en una carpeta dentro del proyecto (Excel, lo que sea)"*).
* **Solución y precauciones técnicas:**
  - La base de datos es la única fuente de la verdad; los tickets deben poder regenerarse al vuelo.
  - Mantener los archivos físicos en `instance/pdfs/` (excluido en `.gitignore`) para no inflar el repositorio Git.
  - Para exportaciones a Excel/CSV, generar los reportes en memoria con `io.BytesIO` y retornarlos mediante `send_file()`.

---

### 9. 🚨 Regla de Integridad: Prohibición de borrado del historial de ventas — 🔴 P0
* **Origen:** Consulta en captura WhatsApp (*"¿El historial de ventas se debería borrar cada semana?"*).
* **Dictamen:** **PROHIBIDO.**
* **Justificación técnica y legal:**
  1. Exigencia legal y fiscal de conservación de comprobantes.
  2. Destrucción de reportes financieros históricos, cálculo de utilidades y auditoría de cajeros.
  3. Imposibilidad de atender devoluciones o aclaraciones de clientes.
* **Solución técnica:** La base de datos conserva permanentemente las ventas; la interfaz debe filtrar por defecto únicamente las ventas del día o semana en curso con paginación server-side.

---

### 10. Documentación de entrega: Manual de Usuario y Manual Técnico — 🟠 P1
* **Origen:** Captura WhatsApp (*"Manual de Usuario Pendiente"*, *"Manual Programador/Mantenimiento"*).
* **Entregables:**
  - `docs/MANUAL_USUARIO.md`: Apertura/cierre de turno, flujo de venta en mostrador/mesa, cancelaciones y emisión de cortes.
  - `docs/MANUAL_TECNICO.md`: Arquitectura Flask, variables de entorno (`bd.env`), base de datos MySQL/Aiven, migraciones y suite de pruebas.

---

# 🤖 PARTE 2 — Hallazgos Técnicos y de Seguridad de la IA (Auditoría de Código)

A continuación se detallan los 21 hallazgos técnicos detectados durante la auditoría estática del código fuente original:

## Resumen ejecutivo

El proyecto está bien estructurado para una aplicación POS (Point of Sale) de tamaño mediano. Usa el patrón Application Factory, blueprints bien separados, pool de conexiones, CSRF, rate-limiting y auditoría transaccional. La mayor parte del código de seguridad crítico (SQL parametrizado, hashing con Werkzeug, tokens criptográficos, `secrets.compare_digest`) está correctamente implementado. No obstante, se detectaron **21 puntos de mejora** clasificados por severidad.

---

## 🔴 Problemas Críticos / Alta Severidad

### 1. `autenticacion_bp.py` — Fuga de información de usuarios registrados (líneas 160–162)

**Archivo:** `blueprints/autenticacion_bp.py`, ~línea 161  
**Problema:** En el flujo de recuperación de contraseña, si el correo NO existe se muestra el mensaje `'El correo electrónico no está registrado en nuestro sistema.'`, mientras que si SÍ existe, se redirige a `/verificar-codigo`. Esta diferencia de respuesta es un **oracle de enumeración de correos**: un atacante puede saber si una dirección tiene cuenta.

```python
# ~línea 160
else:
    flash('El correo electrónico no está registrado en nuestro sistema.', 'danger')
```

**Impacto:** Enumeración de cuentas de usuario / privacidad.  
**Solución recomendada:** Mostrar **siempre** el mismo mensaje genérico: `"Si el correo está registrado, recibirás un código"` y redirigir a la misma página en ambas ramas.

---

### 2. `autenticacion_bp.py` — Timing side-channel en recuperación (líneas 131–163)

**Archivo:** `blueprints/autenticacion_bp.py`  
**Problema:** Cuando el correo no existe, el código retorna inmediatamente (sin generar código, sin enviar mail). Cuando sí existe, ejecuta varias operaciones de BD y correo. La diferencia de tiempo de respuesta (~100–500ms) puede confirmar si un correo existe incluso si se unifica el mensaje.

**Solución:** Añadir `time.sleep` constante o ejecutar una operación dummy de longitud similar cuando el correo no existe (p.ej., generar el código de todas formas sin persistirlo).

---

### 3. `autenticacion_bp.py` — Cuenta desactivada revela existencia del usuario (línea 95–97)

**Archivo:** `blueprints/autenticacion_bp.py`, líneas 95–97  
**Problema:** Se muestra el mensaje `'Esta cuenta está desactivada.'` **antes** de verificar la contraseña, revelando que el nombre de usuario existe en la base.

```python
if not usuario_info['activo']:
    flash('Esta cuenta está desactivada. Contacta al administrador.', 'danger')
    return render_template('login.html')
```

**Solución:** Verificar el hash de la contraseña antes de revelar el estado de la cuenta, o usar un mensaje genérico para todos los fallos de login.

---

### 4. `modelsVentas.py` — El método `procesar_venta_completa` relanza la excepción (líneas 587–590)

**Archivo:** `models/modelsVentas.py`, líneas 587–590  
**Problema:** A diferencia de todas las demás funciones del proyecto que capturan excepciones y retornan `False`, `procesar_venta_completa` hace `raise` en el bloque `except`. Esto significa que errores internos de BD (deadlocks, timeouts) llegan al handler de la ruta como excepciones no controladas, lo que puede filtrar stack traces si `DEBUG=True` en producción, o generar respuestas HTTP 500 inesperadas.

```python
except Exception as e:
    conn.rollback()
    logger.error(f"Error al procesar venta: {e}")
    raise  # ← inconsistente con el resto del código
```

**Solución:** Retornar `(False, "Error interno al procesar la venta", None)` en lugar de relanzar, consistente con el resto de los modelos. La ruta ya tiene su propio handler de `Exception` que devuelve 500.

---

### 5. `ventas_bp.py` — Sin límite superior en `por_pagina` (línea 148)

**Archivo:** `blueprints/ventas_bp.py`, línea 148  
**Problema:** El parámetro `por_pagina` acepta cualquier valor entero sin cota superior. Un atacante autenticado podría solicitar `?por_pagina=1000000` generando una consulta que devuelve millones de filas.

```python
por_pagina = request.args.get('por_pagina', 15, type=int)
# No hay validación de máximo
```

**Solución:**
```python
por_pagina = min(max(request.args.get('por_pagina', 15, type=int), 1), 100)
```

---

## 🟠 Problemas Importantes / Media-Alta Severidad

### 6. `usuarios_bp.py` — Sin validación de formato de correo electrónico (líneas 59, 243)

**Archivos:** `blueprints/usuarios_bp.py` líneas 59 y 243; `blueprints/autenticacion_bp.py` línea 126  
**Problema:** Los campos `correo` se sanean (strip, lower) pero nunca se valida si tienen formato de e-mail válido (`x@y.z`). No hay `re.match` ni librería de validación.

**Impacto:** Se pueden crear usuarios con correos mal formados, lo que causa errores silenciosos en el envío de correos.  
**Solución:** Agregar una función `validar_formato_correo(correo)` en `utils.py` usando `re.match(r'^[^@]+@[^@]+\.[^@]+$', correo)` o mejor, la librería `email-validator`.

---

### 7. `modelsProductos.py` — Uso de `SELECT *` (líneas 41, 57, 69, 100, 216)

**Archivo:** `models/modelsProductos.py`, múltiples líneas  
**Problema:** Varias consultas usan `SELECT *` o `SELECT p.*, c.categoria`. Esto:
- Trae columnas innecesarias (mayor ancho de banda, memoria)
- Si se agrega una columna sensible a la tabla en el futuro, se filtraría automáticamente a la API
- Rompe consultas si se renombra/elimina una columna

```python
cursor.execute("SELECT * FROM tcategorias ORDER BY categoria")  # línea 57
cursor.execute("SELECT * FROM ttamanos ORDER BY Id")             # línea 69
cursor.execute("SELECT p.*, c.categoria FROM ...")               # líneas 41, 216
cursor.execute("SELECT pv.*, t.tamano FROM ...")                 # línea 100
```

**Solución:** Especificar columnas explícitas en todas las consultas.

---

### 8. `modelsProductos.py` — Fuga del mensaje de error interno (línea 191)

**Archivo:** `models/modelsProductos.py`, línea 191  
**Problema:** En `actualizar_producto`, el mensaje de error incluye la excepción interna:

```python
return False, f"Error al actualizar producto: {e}"
```

Esto puede filtrar detalles de la BD (nombres de tablas, columnas, errores de MySQL) hacia el cliente a través de la API.  
**Solución:** Loguear `e` pero retornar un mensaje genérico: `"No se pudo actualizar el producto"`.

---

### 9. `modelsHistorial.py` — Construcción dinámica de SQL sin protección (líneas 33–61)

**Archivo:** `models/modelsHistorial.py`, líneas 33–61  
**Problema:** Aunque los parámetros se pasan correctamente mediante placeholders `%s`, la cláusula `WHERE` se construye mediante concatenación de strings (`where_clause += " AND ..."`) y el `{where_clause}` se inserta en f-strings. Si en alguna refactorización futura alguien confundiera este patrón e insertara un valor directamente, habría inyección SQL. El patrón es frágil y difícil de auditar.

**Solución preferida:** Usar una librería de construcción de queries (p.ej., SQLAlchemy Core expressions) o al menos refactorizar a una lista de condiciones y `" AND ".join(conditions)` con una lista separada de params — lo cual ya se hace, pero la mezcla con f-strings es un antipatrón que genera deuda técnica.

---

### 10. `app.py` — CSP permite `'unsafe-inline'` para scripts (línea 105)

**Archivo:** `app.py`, línea 104–106  
**Problema:** La directiva `Content-Security-Policy` incluye `script-src 'self' 'unsafe-inline'`. Esto anula casi completamente la protección contra XSS que ofrece una CSP, ya que permite ejecutar cualquier script inline.

```python
"script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com"
```

**Solución:** Usar **nonces** (generados por request en Flask) o **hashes SHA256** de los scripts inline específicos, eliminando `'unsafe-inline'`. Flask-Talisman facilita esto.

---

### 11. `config.py` — `SESSION_COOKIE_SAMESITE = 'Lax'` en producción

**Archivo:** `config.py`, línea 7  
**Problema:** `SameSite=Lax` protege contra algunos ataques CSRF, pero no contra navegación cross-site top-level con métodos POST no seguros. Dado que el proyecto usa Flask-WTF para CSRF, esto es una doble capa, pero en `ProductionConfig` debería considerarse `SameSite=Strict` para mayor rigor.

---

### 12. `bd.py` — Pool con `maxcached=5` y `maxconnections=10`

**Archivo:** `bd.py`, líneas 50–53  
**Problema potencial:** `maxcached=5` (conexiones mantenidas al cerrar) con `maxconnections=10` y `blocking=True` puede causar deadlocks de aplicación bajo carga alta si 10 threads aguardan una conexión del pool. En entornos cloud (Aiven), el límite de conexiones MySQL suele ser bajo (10–25). Si la app escala con Gunicorn multi-workers, cada worker tiene su propio pool (`10 conexiones × N workers`), lo que agotaría el límite de la BD rápidamente.

**Solución:** Documentar la relación `workers × pool_size ≤ max_connections_BD` o usar `maxconnections` más pequeño por worker, o considerar PgBouncer/ProxySQL.

---

## 🟡 Problemas Moderados / Deuda Técnica

### 13. `modelsUsuarios.py` — Marcador `__CAMBIO_CORREO__` como prefijo en campo `usuario` (líneas 152–154, 332)

**Archivo:** `models/modelsUsuarios.py`, líneas 152–154 y 332  
**Problema:** La distinción entre "nuevo usuario" y "cambio de correo" se hace insertando `'__CAMBIO_CORREO__{id}'` en la columna `usuario` de `tvalidacion_usuarios`. Esto es un **antipatrón de diseño** que combina datos de control con datos de dominio:
- Si alguien crea un usuario con el nombre literalmente `__CAMBIO_CORREO__5`, colisionaría con la lógica.
- El campo `usuario` varchar para almacenar un ID entero es semánticamente incorrecto.

**Solución recomendada:** Agregar una columna `tipo_validacion` (`ENUM('alta', 'cambio_correo')`) y `usuario_existente_id INT NULL` a `tvalidacion_usuarios`.

---

### 14. `modelsLimpieza.py` — Limpieza solo al arrancar, no periódica

**Archivo:** `models/modelsLimpieza.py` + `app.py`, líneas 155–157  
**Problema:** Las funciones de limpieza de registros expirados (`limpiar_validaciones_expiradas`, `limpiar_codigos_recuperacion_expirados`) se llaman **solo al arrancar la aplicación** en modo `__main__`. En producción con Waitress/Gunicorn, la aplicación raramente reinicia, por lo que la tabla `tvalidacion_usuarios` puede acumular miles de registros expirados.

**Solución:** Usar `APScheduler` o un cron de MySQL (`EVENT`) para ejecutar la limpieza periódicamente (p.ej., cada hora).

---

### 15. `productos_bp.py` — Sin eliminación de imagen antigua al actualizar producto (líneas 112–116)

**Archivo:** `blueprints/productos_bp.py`, líneas 112–116  
**Problema:** Cuando se actualiza un producto y se sube una nueva imagen, la imagen anterior no se elimina del sistema de archivos (`/static/images/productos/`). Con el tiempo esto puede consumir espacio significativo en disco.

**Solución:** Antes de guardar la nueva imagen, obtener la ruta actual del producto y eliminar el archivo anterior si existe (`os.remove`).

---

### 16. `modelsInventario.py` — Lógica de alertas hardcodeada con constantes mágicas (líneas 52–67)

**Archivo:** `models/modelsInventario.py`, líneas 52–67  
**Problema:** Los umbrales de alerta de inventario (`stock_minimo + 5` y `stock_minimo + 10`) están hardcodeados en el SQL.

```sql
AND p.stock <= p.stock_minimo + 5  -- ¿Por qué 5?
AND p.stock <= p.stock_minimo + 10 -- ¿Por qué 10?
```

**Solución:** Mover estos umbrales a configuración (`bd.env` o `config.py`) como `STOCK_ALERT_CRITICAL_OFFSET` y `STOCK_ALERT_NORMAL_OFFSET`.

---

### 17. `modelsVentas.py` — Consulta a `information_schema` por cada llamada (líneas 11–21)

**Archivo:** `models/modelsVentas.py`, función `_detalle_tiene_variante_id`, líneas 11–21  
**Problema:** Esta función consulta `information_schema.COLUMNS` en **cada operación** de lectura o escritura de ventas (llamada en `obtener_detalle_orden`, `obtener_venta_completa`, `procesar_venta_completa`). Consultar `information_schema` es una operación costosa en MySQL (full scan interno) y no debería ejecutarse en hot paths.

**Solución:** Cachear el resultado en una variable de módulo (`_has_variante_id = None`) con doble-checked locking, o —mejor— eliminar la compatibilidad hacia atrás y asumir que la migración ya se aplicó (enforcing `apply_migrations.py`).

---

### 18. `finanzas_bp.py` — Ruta de búsqueda de PDF con parámetros en la URL (línea 137)

**Archivo:** `blueprints/finanzas_bp.py`, línea 137  
**Problema:** La ruta `/buscar_pdf_corte/<fecha_inicio>/<fecha_fin>` acepta dos parámetros de ruta de texto libre. Aunque se validan con regex, el uso de `path` en el converter puede introducir ambigüedad. El problema principal es que la búsqueda de archivos PDF usa una **coincidencia parcial** (`f_inicio_limpia in archivo`), lo que podría retornar un archivo incorrecto si dos fechas comparten prefijo.

**Solución:** Buscar el PDF por ID de corte (que se almacena en `tcortescaja.Id`) en lugar de por fechas en el nombre del archivo, garantizando unicidad.

---

### 19. `extensions.py` — Rate limiter usa `memory://` por defecto en producción

**Archivo:** `extensions.py`, `config.py` línea 28  
**Problema:** La configuración por defecto de `RATELIMIT_STORAGE_URI=memory://` no persiste entre reinicios ni funciona correctamente con múltiples workers. En producción con Waitress o Gunicorn multi-process, cada worker tiene su propio contador, haciendo inefectivo el rate limiting.

**Impacto:** Un atacante puede evadir el rate limiting distribuyendo peticiones entre workers.  
**Solución:** Requerir Redis en producción. `bd.env.example` ya lo menciona, pero no se valida que Redis esté configurado cuando `APP_ENV=NUBE`.

---

### 20. `pyproject.toml` — Ruff con reglas muy limitadas (línea 13)

**Archivo:** `pyproject.toml`, línea 13  
**Problema:** La configuración de Ruff solo activa 4 categorías de reglas:
```toml
select = ["E9", "F63", "F7", "F82"]
```
Esto solo detecta errores de sintaxis y referencias a nombres no definidos. No detecta problemas de seguridad, complejidad, bugs comunes ni estilo. Se pierde el valor principal de Ruff.

**Solución recomendada:**
```toml
select = ["E", "F", "W", "B", "S", "C90", "I", "N", "UP"]
# B = Bugbear, S = Bandit-like security, C90 = complejidad, I = isort
```

---

## 🟢 Mejoras de Calidad / Refactoring

### 21. `utils.py` — Validación de contraseña incompleta (líneas 107–117)

**Archivo:** `utils.py`, líneas 107–117  
**Problema:** La validación de contraseñas solo exige longitud ≥8, mayúscula, minúscula y dígito. No verifica:
- Longitud máxima (contraseñas de >1000 chars pueden ser un ataque DoS a bcrypt)
- Caracteres especiales (la política es relativamente débil)
- Listas de contraseñas comunes (HIBP, rockyou)

**Solución:** Agregar `if len(contrasena) > 128: return False, "Contraseña demasiado larga"` como mínimo.

---

### 22. `modelsProductos.py` — Función `agregar_variante_producto` sin rollback (líneas 77–93)

**Archivo:** `models/modelsProductos.py`, líneas 77–93  
**Problema:** La función `agregar_variante_producto` no tiene `conn.rollback()` en el bloque except — solo loguea el error y retorna False. Si hay una excepción parcial entre el INSERT y el `registrar_evento`, la transacción queda en estado indeterminado hasta que la conexión se devuelva al pool.

```python
except Exception as e:
    logger.error(f"Error al agregar variante: {e}")
    return False  # ← falta conn.rollback()
```

**Solución:** Agregar `conn.rollback()` en todos los bloques `except` de funciones que hacen escrituras (revisar también `eliminar_variantes_producto` línea 129).

---

### 23. `modelsVentas.py` — `procesar_venta_completa` con función excesivamente larga (>250 líneas)

**Archivo:** `models/modelsVentas.py`, función `procesar_venta_completa`  
**Problema:** La función tiene ~265 líneas de código con múltiples responsabilidades: validación de entrada, validación de negocio, consultas a BD, cálculos financieros, registro de movimientos. Esto la hace difícil de leer, probar unitariamente y mantener.

**Solución:** Extraer subfunciones: `_validar_productos_request()`, `_verificar_stock()`, `_calcular_total()`, `_registrar_detalle_venta()`.

---

### 24. `modelsHistorial.py` — Sin validación de `fecha_inicio`/`fecha_fin` (líneas 24–30)

**Archivo:** `models/modelsHistorial.py`, líneas 24–30  
**Problema:** Los filtros de fecha se pasan directamente al SQL sin validar el formato. Si `fecha_inicio` tiene un formato inesperado, MySQL puede ignorar el filtro silenciosamente o arrojar un error.

**Solución:** Validar el formato antes de construir la query:
```python
try:
    datetime.strptime(fecha_inicio, '%Y-%m-%d')
except ValueError:
    fecha_inicio = None
```

---

## 📦 Dependencias y Configuración

### 25. `requirements.txt` — Dependencia `redis` instalada pero opcional (línea 9)

**Archivo:** `requirements.txt`, línea 9  
**Problema:** `redis==8.1.0` está en las dependencias de producción, pero solo se usa si `RATELIMIT_STORAGE_URI` apunta a Redis. En entornos locales sin Redis instalado, la librería ocupa espacio sin ser usada.

**Mejora:** Mover a `requirements-dev.txt` o crear un `requirements-prod.txt` separado con Redis. Alternativamente, documentar que Redis es requerido en producción.

---

### 26. `requirements-dev.txt` — `python-docx` en dependencias de desarrollo

**Archivo:** `requirements-dev.txt`, línea 5  
**Problema:** `python-docx==1.2.0` aparece en las dependencias de desarrollo pero se usa en `scripts/gen_docx.py` (generación de documentación). Esto es correcto, pero el script no está integrado en el pipeline de CI ni documentado. Si se usa para generar artefactos de entrega, debería estar documentado en el README.

---

### 27. `apply_migrations.py` — Sin registro de migración aplicada en `tschema_migrations` (líneas 110–121)

**Archivo:** `scripts/apply_migrations.py`, líneas 110–121  
**Problema crítico:** El script aplica las migraciones SQL y hace `commit`, pero **nunca inserta el registro en `tschema_migrations`**. Si se vuelve a ejecutar `apply_migrations.py`, todas las migraciones se aplicarán de nuevo porque `applied` estará vacío.

```python
for version, path in pending:
    script = path.read_text(encoding='utf-8-sig')
    try:
        for statement in split_sql(script):
            cursor.execute(statement)
        connection.commit()
        completed.append(path.name)
        # ← FALTA: INSERT INTO tschema_migrations (version, nombre) VALUES (...)
```

**Impacto:** Re-aplicar migraciones puede corromper datos o duplicar columnas.  
**Solución:** Agregar el INSERT después de aplicar cada migración.

---

## 🧪 Cobertura de Pruebas

### 28. Tests de integración están desactivados por defecto

**Problema:** Las pruebas de integración requieren `RUN_DB_WRITE_TESTS=1` y una BD de test. La CI solo ejecuta `pytest -m "not integration"`, dejando sin probar automáticamente los flujos reales de BD: ventas, cortes de caja, migraciones.

**Recomendación:** Configurar un job de CI separado con MySQL service (GitHub Actions admite `services: mysql`) que ejecute `pytest -m integration`.

### 29. Sin pruebas para `modelsInventario.contar_alertas_inventario`

La función es llamada en **cada request autenticado** (context processor en `app.py`, línea 88) pero no tiene pruebas unitarias directas con escenarios de umbral (stock exactamente en el límite, por encima, por debajo).

### 30. `services/auditoria.py` no incluido en cobertura requerida

**Archivo:** `pyproject.toml`, líneas 25–33  
La carpeta `services/` no aparece en `[tool.coverage.report] include`. El archivo `services/auditoria.py` no contribuye al `fail_under = 100`.

---

## 📊 Resumen de Hallazgos

| # | Categoría | Severidad | Archivo | Descripción |
|---|-----------|-----------|---------|-------------|
| 1 | Seguridad | 🔴 Alta | `autenticacion_bp.py:161` | Oracle de enumeración de correos |
| 2 | Seguridad | 🔴 Alta | `autenticacion_bp.py:131` | Timing side-channel en recuperación |
| 3 | Seguridad | 🔴 Alta | `autenticacion_bp.py:95` | Cuenta desactivada revela existencia |
| 4 | Rendimiento/Error | 🔴 Alta | `modelsVentas.py:590` | Excepción relanzada inconsistentemente |
| 5 | Seguridad/Rendimiento | 🔴 Alta | `ventas_bp.py:148` | Sin límite en `por_pagina` |
| 6 | Validación | 🟠 Media | Múltiples | Sin validación de formato de correo |
| 7 | Rendimiento/Seguridad | 🟠 Media | `modelsProductos.py` | `SELECT *` en producción |
| 8 | Seguridad | 🟠 Media | `modelsProductos.py:191` | Fuga de error interno de BD |
| 9 | Deuda técnica | 🟠 Media | `modelsHistorial.py` | SQL dinámico con f-strings |
| 10 | Seguridad | 🟠 Media | `app.py:105` | CSP con `unsafe-inline` para scripts |
| 11 | Seguridad | 🟠 Media | `config.py` | SameSite=Lax en producción |
| 12 | Rendimiento | 🟠 Media | `bd.py:50` | Pool sin validar límite por workers |
| 13 | Diseño | 🟡 Moderado | `modelsUsuarios.py:152` | Antipatrón de marcador en campo usuario |
| 14 | Mantenibilidad | 🟡 Moderado | `modelsLimpieza.py` | Limpieza solo al arrancar |
| 15 | Funcional | 🟡 Moderado | `productos_bp.py:112` | Imágenes huérfanas sin eliminar |
| 16 | Configuración | 🟡 Moderado | `modelsInventario.py:56` | Constantes mágicas en umbrales |
| 17 | Rendimiento | 🟡 Moderado | `modelsVentas.py:11` | `information_schema` en hot paths |
| 18 | Funcional | 🟡 Moderado | `finanzas_bp.py:137` | Búsqueda PDF por fecha parcial |
| 19 | Seguridad/Config | 🟡 Moderado | `extensions.py` | Rate limiter en memoria en producción |
| 20 | Calidad | 🟡 Moderado | `pyproject.toml:13` | Ruff con reglas mínimas |
| 21 | Seguridad | 🟢 Baja | `utils.py:107` | Sin límite máximo de contraseña |
| 22 | Robustez | 🟢 Baja | `modelsProductos.py:90` | Falta `rollback()` en variantes |
| 23 | Mantenibilidad | 🟢 Baja | `modelsVentas.py` | Función >265 líneas |
| 24 | Validación | 🟢 Baja | `modelsHistorial.py:24` | Sin validación de formato de fechas |
| 25 | Dependencias | 🟢 Baja | `requirements.txt:9` | `redis` siempre instalado |
| 26 | Documentación | 🟢 Baja | `requirements-dev.txt:5` | `python-docx` sin documentar |
| 27 | **Bug** | 🔴 **Crítico** | `apply_migrations.py:117` | Migraciones nunca se registran en tracking table |
| 28 | Pruebas | 🟠 Media | CI | Pruebas de integración no automatizadas |
| 29 | Pruebas | 🟡 Moderado | `tests/` | Sin tests para `contar_alertas_inventario` |
| 30 | Pruebas | 🟡 Moderado | `pyproject.toml` | `services/` no incluido en cobertura |

---

## ✅ Aspectos Bien Implementados

- **SQL parametrizado** consistente en todos los modelos (no hay inyección SQL directa)
- **Werkzeug `generate_password_hash`/`check_password_hash`** correctamente usado
- **`secrets.compare_digest`** para comparación de códigos OTP (resistente a timing attacks en la verificación del código en sí)
- **CSRF** con Flask-WTF activado y correctamente manejado
- **Rate limiting** en endpoints sensibles (login, recuperación, validación)
- **`FOR UPDATE`** en transacciones de ventas y recuperación (previene race conditions)
- **Batch query** para variantes de productos (evita N+1 en menú y gestión)
- **Application Factory** bien implementada con separación de responsabilidades
- **Auditoría transaccional** en todas las operaciones críticas
- **Rollback** adecuado en la mayoría de transacciones de escritura
- **SSL/TLS** verificado en conexión a BD en producción (Aiven)
- **Validación de firma de imagen** (magic bytes) antes de guardar
- **`secure_filename`** y extensiones permitidas para uploads
- **Sesión con versión** (`sesion_version`) para invalidar sesiones activas al cambiar contraseña
- **Headers de seguridad** HTTP completos (X-Frame-Options, X-Content-Type-Options, HSTS, CSP)
- **Cobertura del 100%** requerida en CI para código de producción
