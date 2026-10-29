# Guía y Reglas para Agentes de IA — Coffee Hacienda POS

Este documento establece las directrices de desarrollo, reglas de negocio no negociables y el protocolo de comunicación para cualquier agente de IA que trabaje en el código de **Coffee Hacienda POS**.

---

## 1. Protocolo de Comunicación y Consulta (Regla de Oro)

1. **Preguntar ante la duda:** Siempre que haya ambigüedad, decisiones de lógica de negocio o definición de valores (montos, tiempos límite, umbrales de stock, IDs de estado, etc.), el agente **debe consultar al desarrollador/usuario antes de asumir o escribir código**.
2. **Recomendación fundamentada:** Al hacer una consulta o plantear alternativas, el agente debe **proporcionar siempre una recomendación clara, justificada y con opciones concretas**, explicando ventajas y posibles riesgos técnicos o contables.
3. **No ejecutar suposiciones destructivas:** Si una instrucción puede interpretarse de varias maneras, pedir confirmación antes de modificar esquemas o borrar archivos.

---

## 2. Reglas de Negocio e Integridad Contable (No Negociables)

1. **Inmutabilidad del Historial de Ventas:**
   * **NUNCA borrar ni truncar ventas ni sus detalles.**
   * Las transacciones comerciales son legal, fiscal y contablemente inmutables.
   * Para no saturar las interfaces, la solución es **filtrar por fecha** (día actual, semana en curso) y paginar en el servidor.
2. **Corte de Caja Continuo (Sin Huecos):**
   * El corte más actual **solo puede realizarse a partir del último corte registrado**.
   * La `fecha_hora_inicio` del nuevo corte debe coincidir exactamente con la `fecha_hora_cierre` del corte inmediato anterior (`SELECT MAX(fecha_hora_cierre) FROM tcortescaja`).
   * El campo `fechaDesde` en la interfaz debe estar bloqueado (`readonly`).
3. **Auditoría Obligatoria y Trazabilidad:**
   * Toda acción que altere el inventario (`AJUSTAR_STOCK`, máximos, mínimos), cancele una venta (`CANCELAR`) o registre dinero (`CREAR corte_caja`) debe quedar asentada en la tabla `tauditoria` con el `usuario_id`, fecha y los detalles del motivo.
4. **Confirmación con Motivo en Acciones Críticas:**
   * Ninguna cancelación de pedido o ajuste manual de existencias debe realizarse con un solo clic. La interfaz debe exigir un modal de confirmación con campo obligatorio para capturar el motivo.
5. **Normalización de Servicio y Mesas:**
   * El servicio por defecto siempre es `"Para llevar"`. Las opciones de comedor deben estar delimitadas a las mesas físicas disponibles (ej. `"Mesa 1"` a `"Mesa 5"` o `"Barra"`), eliminando entradas ambiguas como `"Sin mesa"`.

---

## 3. Base de Datos y Entornos (Dual MySQL)

1. **Entorno Dual:**
   * **Local:** MAMP / MySQL 5.7 o 8.0 en `127.0.0.1:3306`, base de datos `bd`.
   * **Nube:** Aiven MySQL gestionado con conexión TLS obligatoria (`DB_SSL_CA`).
2. **Cero cambios manuales en Aiven:**
   * Cualquier alteración de esquema debe documentarse y aplicarse mediante scripts de migración versionados en `database/migraciones/`.
   * Primero se prueba y valida en local, se genera respaldo y después se aplica en la nube.
3. **Consultas 100% Parametrizadas:**
   * Prohibida la concatenación de variables en sentencias SQL (`%s` obligatorio).
   * No usar `SELECT *` o `u.*` en tablas de usuarios para evitar fugas de hashes o datos sensibles.
4. **Transacciones Robustas:**
   * Toda operación de escritura múltiple debe usar bloques `try ... except` con `conn.rollback()` explícito y `conn.commit()`.
   * Concurrencia protegida mediante `SELECT ... FOR UPDATE` en operaciones de stock y ventas.

---

## 4. Seguridad, Secretos y Manejo de Archivos

1. **Secretos y Credenciales:**
   * Nunca guardar contraseñas, tokens de correo ni claves en el código fuente.
   * El archivo `bd.env` contiene secretos reales y **jamás debe versionarse en Git** (debe permanecer en `.gitignore`).
   * Mantener siempre actualizado `bd.env.example` solo con valores ficticios.
2. **Validación y Cotas de Entrada:**
   * Todo parámetro recibido en query o JSON debe validarse y sanitizarse.
   * Parámetros de paginación (`por_pagina`) deben acotarse estrictamente (ej. `min(max(por_pagina, 1), 100)`).
3. **Almacenamiento de Comprobantes:**
   * Los tickets en PDF y cortes de caja físicos se guardan en la carpeta `instance/pdfs/` (ignorada en Git) o se generan dinámicamente en memoria con `io.BytesIO`.
   * Nunca comitear PDFs o Excels generados al repositorio.

---

## 5. Pruebas y Control de Calidad

1. **No romper la suite de pruebas:**
   * Antes de dar por concluido un cambio relevante, verificar que las pruebas unitarias pasen (`pytest`).
   * Si se altera una función o ruta, actualizar o agregar su correspondiente prueba unitaria manteniendo la cobertura.
2. **Historial de Git Limpio:**
   * Respetar las convenciones semánticas definidas en `docs/desarrollo/GUIA_COMMITS.md` (`feat:`, `fix:`, `refactor:`, `docs:`, etc.).
   * Mantener ramas sincronizadas con `git pull` antes de comenzar trabajo nuevo.

---

## 6. Evolución Continua y Documento Vivo (Apertura a Mejoras)

1. **Documento Vivo y Adaptable:**
   * Este archivo `AGENTS.md` **no es estático**. Está permanentemente abierto a mejoras, ampliaciones, nuevas reglas operativas o ajustes acordados entre el desarrollador y los agentes de IA.
   * Cualquier nuevo criterio contable, convención técnica o regla de negocio validada debe integrarse y versionarse en este documento.
2. **Proactividad y Mejora Continua del Sistema:**
   * El código y la arquitectura del sistema están en constante optimización. Si un agente detecta áreas de oportunidad (rendimiento, seguridad, usabilidad en caja, simplificación de flujos), debe proponerlas constructivamente.
   * Las propuestas de mejora para el sistema deben ser consultadas y validadas con el usuario siguiendo el **Protocolo de Consulta (Sección 1)** antes de realizar modificaciones.
3. **Ciclo de Aprendizaje:**
   * Cuando el desarrollador corrija, defina o ajuste una preferencia de trabajo, el agente debe actualizar `AGENTS.md` para que la directriz quede registrada de forma permanente para futuras sesiones.

