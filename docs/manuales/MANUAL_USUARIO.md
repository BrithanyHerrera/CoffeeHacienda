# ☕ Manual de Usuario — Coffee Hacienda POS

> **Versión:** 1.0 | **Fecha:** Noviembre 2026 | **Sistema:** Coffee Hacienda POS

---

## 📖 Tabla de Contenidos

1. [¿Qué es Coffee Hacienda POS?](#-qué-es-coffee-hacienda-pos)
2. [Roles del Sistema](#-roles-del-sistema)
3. [URL de Acceso](#-url-de-acceso)
4. [Inicio de Sesión](#1-inicio-de-sesión)
5. [Dashboard / Página Principal](#2-dashboard--página-principal)
6. [Punto de Venta — Menú](#3-punto-de-venta--menú)
7. [Monitor de Órdenes](#4-monitor-de-órdenes)
8. [Historial de Ventas](#5-historial-de-ventas)
9. [Inventario (Solo Admin)](#6-inventario-solo-admin)
10. [Corte de Caja (Solo Admin)](#7-corte-de-caja-solo-admin)
11. [Reportes Financieros (Solo Admin)](#8-reportes-financieros-solo-admin)
12. [Gestión de Productos (Solo Admin)](#9-gestión-de-productos-solo-admin)
13. [Gestión de Usuarios (Solo Admin)](#10-gestión-de-usuarios-solo-admin)
14. [Procedimiento de Cierre del Día](#11-procedimiento-de-cierre-del-día)
15. [Preguntas Frecuentes / Solución de Problemas](#12-preguntas-frecuentes--solución-de-problemas)

---

## 🏪 ¿Qué es Coffee Hacienda POS?

**Coffee Hacienda POS** es el sistema de Punto de Venta (POS) diseñado específicamente para la cafetería **La Hacienda**, ubicada en Haciendas de San Vicente, 63737 San Vicente, Nay. Su objetivo es digitalizar y agilizar las operaciones diarias del negocio, incluyendo:

- 📋 **Toma de órdenes** en mesa o para llevar
- 💰 **Registro y control de ventas** con múltiples métodos de pago
- 🛒 **Monitoreo en tiempo real** de las órdenes activas
- 🏷️ **Control de inventario** con alertas de stock bajo
- 📊 **Reportes financieros** y cortes de caja auditables
- 👥 **Gestión de usuarios** con control de acceso por rol

El sistema corre localmente en el navegador web y está construido sobre **Flask (Python)** con base de datos **MySQL**, con soporte para entorno local (MAMP) y en la nube (Aiven).

---

## 👥 Roles del Sistema

El sistema maneja dos roles de usuario con permisos diferenciados:

| Funcionalidad | 🧑‍💼 Administrador | 🧑‍🍳 Vendedor |
|---|:---:|:---:|
| Ver Dashboard / Página Principal | ✅ | ✅ |
| Punto de Venta (Menú) | ✅ | ✅ |
| Monitor de Órdenes | ✅ | ✅ |
| Historial de Ventas | ✅ | ✅ |
| Gestión de Productos | ✅ | ❌ |
| Gestión de Usuarios | ✅ | ❌ |
| Inventario | ✅ | ❌ |
| Corte de Caja | ✅ | ❌ |
| Reportes Financieros | ✅ | ❌ |

> [!IMPORTANT]
> Las opciones exclusivas del Administrador **no aparecen en el menú lateral** cuando un Vendedor ha iniciado sesión. Esta restricción es por diseño y no puede eludirse.

### 🧑‍💼 Rol Administrador
Tiene acceso completo al sistema. Es responsable de:
- Crear y gestionar usuarios
- Realizar el corte de caja al fin del turno o del día
- Revisar los reportes financieros
- Controlar el inventario y los productos del catálogo

### 🧑‍🍳 Rol Vendedor
Acceso limitado al flujo operativo de ventas:
- Registrar nuevas ventas desde el Menú
- Consultar el estado de las órdenes activas
- Consultar el Historial de Ventas (solo lectura)

---

## 🌐 URL de Acceso

El sistema se accede directamente desde cualquier navegador web moderno en la misma red local donde esté ejecutándose el servidor:

```
http://127.0.0.1:5000
```

> [!NOTE]
> Si accedes desde otro dispositivo en la misma red, reemplaza `127.0.0.1` por la dirección IP local del equipo servidor (ej. `http://192.168.1.10:5000`). Consulta al administrador de red o de sistemas para obtener la IP correcta.

---

## 1. 🔐 Inicio de Sesión

### 1.1 Pantalla de Login

Al ingresar a la URL del sistema, se muestra la pantalla de inicio de sesión con los siguientes campos:

| Campo | Descripción |
|---|---|
| **Usuario / Correo** | Nombre de usuario o correo electrónico registrado |
| **Contraseña** | Contraseña asignada (mínimo 8 caracteres, debe incluir letras, números y al menos un símbolo) |

**Pasos para iniciar sesión:**
1. Escribe tu nombre de usuario o correo en el campo correspondiente.
2. Escribe tu contraseña.
3. Haz clic en el botón **Iniciar Sesión**.
4. Si los datos son correctos, serás redirigido automáticamente a la **Página Principal (Dashboard)**.

> [!WARNING]
> Si ingresas datos incorrectos, el sistema mostrará un mensaje de error. Verifica tu usuario y contraseña antes de intentarlo de nuevo.

---

### 1.2 Recuperación de Contraseña por Email

Si olvidaste tu contraseña, el sistema ofrece un proceso de recuperación en **3 pasos**:

#### Paso 1 — Solicitar recuperación
1. En la pantalla de Login, haz clic en **"¿Olvidaste tu contraseña?"**.
2. Ingresa el **correo electrónico** asociado a tu cuenta.
3. Haz clic en **"Enviar código"**.
4. El sistema enviará un correo con un **código de verificación** a la dirección indicada.

> [!TIP]
> Revisa también tu carpeta de **Spam o Correo no deseado** si no ves el correo en tu bandeja de entrada.

#### Paso 2 — Ingresar el código de verificación
1. Abre el correo recibido y copia el código de verificación.
2. En la pantalla del sistema, ingresa el código en el campo correspondiente.
3. Haz clic en **"Verificar código"**.

#### Paso 3 — Establecer nueva contraseña
1. Una vez verificado el código, escribe tu **nueva contraseña** (mínimo 8 caracteres, con letras, números y un símbolo).
2. Confirma la nueva contraseña en el campo de confirmación.
3. Haz clic en **"Guardar nueva contraseña"**.
4. El sistema te redirigirá al Login para que inicies sesión con tu nueva contraseña.

---

### 1.3 Cuenta Desactivada

Si un Administrador ha **desactivado tu cuenta**, verás un mensaje indicando que tu acceso está suspendido. En ese caso:

- **No podrás iniciar sesión** hasta que un Administrador reactive tu cuenta.
- Contacta al Administrador del sistema para solicitar la reactivación.

> [!CAUTION]
> Las cuentas desactivadas **no se eliminan del sistema**. El Administrador puede reactivarlas en cualquier momento desde la sección **Gestión de Usuarios**.

---

## 2. 🏠 Dashboard / Página Principal

### Acceso
- **URL:** `http://127.0.0.1:5000/bienvenida`
- **Menú lateral:** 🏠 Página Principal

### ¿Qué muestra?

La página principal sirve como **punto de bienvenida** y hub de acceso rápido al sistema. Muestra información relevante según el rol del usuario autenticado.

#### Información general visible:
- **Nombre del usuario** autenticado (mostrado en la barra superior de cada módulo)
- **Accesos directos** a las secciones más usadas según el rol

#### 🔴 Alertas de Stock Bajo (Solo Administrador)
En el menú lateral izquierdo, el enlace de **🏷️ Inventario** mostrará un **punto rojo de alerta** (`●`) cuando uno o más productos tengan existencias en estado **CRÍTICO** o **ALERTA**.

```
🏷️ Inventario  🔴
```

Esta alerta es visible desde cualquier pantalla del sistema (ya que el sidebar es persistente), lo que permite al Administrador actuar rápidamente ante problemas de stock sin necesidad de navegar activamente al módulo de Inventario.

### 🗺️ Navegación lateral (Sidebar)

El menú lateral es accesible desde cualquier pantalla. Se despliega o colapsa con el botón **☰ Menú** (en móviles).

**Opciones visibles para Vendedor:**
- 🏠 Página Principal
- 📋 Menú
- 🛒 Órdenes
- 📜 Historial
- 🚪 Salir

**Opciones adicionales para Administrador:**
- 📝 Gestión Productos
- 🤝 Gestión Usuarios
- 🏷️ Inventario *(con alerta visual si hay stock crítico)*
- 💵 Corte de Caja
- 💰 Reportes de Ventas

---

## 3. 📋 Punto de Venta — Menú

### Acceso
- **URL:** `http://127.0.0.1:5000/menu`
- **Menú lateral:** 📋 Menú
- **Roles:** ✅ Administrador | ✅ Vendedor

### Descripción General

Esta es la pantalla principal para **registrar nuevas ventas**. Está dividida en dos zonas principales:

```
┌──────────────────────────────┬──────────────────┐
│   ZONA DE PRODUCTOS          │   PANEL ORDEN     │
│   (pestañas + búsqueda)      │   (carrito)       │
│                              │                   │
│   [Todas][Café][Bebidas]...  │   • Producto 1    │
│                              │   • Producto 2    │
│   🖼️ Prod.A   🖼️ Prod.B    │   ─────────────   │
│   $precio     $precio        │   Total: $XX.XX   │
│   [Añadir]   [Añadir]        │   Nombre cliente  │
│                              │   Mesa/Servicio   │
│                              │   Método de pago  │
│                              │   [Realizar orden]│
└──────────────────────────────┴──────────────────┘
```

---

### 3.1 Barra de Búsqueda

En la parte superior de la zona de productos hay un campo de búsqueda de texto:

- **Placeholder:** "Buscar..."
- **Función:** Filtra los productos en tiempo real mientras escribes, buscando coincidencias en el **nombre** y la **descripción** del producto.
- **Límite de caracteres:** 50
- El filtro de búsqueda **se combina** con el filtro de categoría activo.

> [!TIP]
> Si buscas "cap" y estás en la pestaña "Café", solo verás los productos de esa categoría cuyo nombre o descripción contengan "cap".

---

### 3.2 Pestañas de Categorías

Debajo del encabezado hay una barra de pestañas horizontales:

| Pestaña | Función |
|---|---|
| **Todas** | Muestra todos los productos activos del catálogo (seleccionada por defecto) |
| **[Categoría 1]** | Filtra y muestra solo los productos de esa categoría |
| **[Categoría 2]** | Filtra y muestra solo los productos de esa categoría |
| *…* | Las categorías se generan dinámicamente según los productos en el catálogo |

- La pestaña activa se resalta visualmente.
- Al hacer clic en una pestaña, el panel de productos se actualiza instantáneamente.

---

### 3.3 Tarjetas de Producto

Cada producto aparece como una tarjeta con:

| Elemento | Descripción |
|---|---|
| 🖼️ **Imagen** | Foto del producto (o imagen genérica si no tiene) |
| **Nombre** | Nombre del producto |
| **Descripción** | Descripción corta del producto |
| **Precio(s) / Tamaño(s)** | Si el producto tiene variantes de tamaño, se listan todas con su precio. Si es un único tamaño, se muestra el precio directo. |
| **[Añadir a la orden]** | Botón para agregar el producto al carrito |

---

### 3.4 Agregar Producto al Carrito

#### Producto con un solo tamaño / precio
1. Haz clic en el botón **"Añadir a la orden"** de la tarjeta.
2. El producto se agrega inmediatamente al carrito con cantidad 1.
3. Si el mismo producto (mismo tamaño) ya está en el carrito, su cantidad se incrementa en 1.

#### Producto con múltiples tamaños (variantes)
1. Haz clic en el botón **"Añadir a la orden"**.
2. Aparece un **modal de selección de tamaño** con los botones de cada variante disponible (ej: "Chico — $25", "Mediano — $35", "Grande — $45").
3. Haz clic en el tamaño deseado.
4. El modal se cierra y el producto con el tamaño seleccionado se agrega al carrito.
5. Para cerrar el modal sin agregar nada, haz clic en la **X** o fuera del modal.

---

### 3.5 Panel de Orden (Carrito — lado derecho)

El panel derecho, **siempre visible**, muestra el contenido actual de la orden en proceso.

#### Items del carrito
Cada producto agregado muestra:
- 🖼️ **Miniatura** de la imagen del producto
- **Nombre** del producto y tamaño seleccionado entre paréntesis
- **Precio unitario**
- **Subtotal** del ítem (precio × cantidad)
- **Campo de cantidad** editable (mínimo: 1) — puedes modificarlo directamente
- **Botón [X]** para eliminar ese ítem del carrito

> [!TIP]
> Para cambiar la cantidad de un producto, haz clic en el campo numérico del ítem en el carrito, edita el valor y el subtotal se recalcula automáticamente. Si pones 0 o un valor inválido, el sistema lo resetea a 1.

#### Total
Al final de los ítems se muestra el **Total acumulado** de la orden, actualizado en tiempo real.

---

### 3.6 Campo: Nombre del Cliente

- **Obligatorio** ⚠️
- Solo acepta **letras y espacios** (no se permiten números)
- Límite: 100 caracteres
- Si se deja vacío y se intenta confirmar la orden, el sistema muestra un error.

---

### 3.7 Selector de Mesa / Servicio

Permite indicar si la orden es para llevar o para una mesa del comedor:

| Opción | Descripción |
|---|---|
| **Para llevar** *(seleccionado por defecto)* | La orden es para consumo fuera del local |
| **Mesa 1** | Mesa del comedor número 1 |
| **Mesa 2** | Mesa del comedor número 2 |
| **Mesa 3** | Mesa del comedor número 3 |
| **Mesa 4** | Mesa del comedor número 4 |
| **Mesa 5** | Mesa del comedor número 5 |

> [!IMPORTANT]
> El sistema normaliza automáticamente cualquier valor inválido como "Sin mesa" o "None" a **"Para llevar"**. Las únicas opciones válidas del comedor son Mesa 1 a Mesa 5.

---

### 3.8 Método de Pago

Selecciona el método con el que el cliente pagará:

| Método | Comportamiento |
|---|---|
| **Efectivo** | Habilita los campos **"Dinero Recibido"** y **"Cambio"** |
| **Tarjeta** | Los campos de Dinero Recibido y Cambio se ocultan automáticamente |
| **Transferencia** | Los campos de Dinero Recibido y Cambio se ocultan automáticamente |

---

### 3.9 Dinero Recibido y Cambio (solo Efectivo)

Cuando el método de pago es **Efectivo**:

1. **Campo "Dinero Recibido":**
   - Ingresa el monto en efectivo que entrega el cliente.
   - Solo acepta valores positivos (sin letras, sin negativos).
   - Máximo: $99,999.99

2. **Campo "Cambio":**
   - Se calcula y muestra **automáticamente** al escribir el monto recibido.
   - Fórmula: `Cambio = Dinero Recibido − Total de la orden`
   - Es de solo lectura (no editable manualmente).

> [!WARNING]
> Si el dinero recibido es **menor al total de la orden**, el sistema bloqueará la venta y mostrará un mensaje de error. No es posible registrar una venta con efectivo insuficiente.

---

### 3.10 Confirmar Venta — Botón "Realizar la Orden"

Una vez que el carrito tenga productos, el nombre del cliente esté completo y el método de pago esté seleccionado:

1. Haz clic en el botón **"Realizar la orden"** (en verde, al final del panel derecho).
2. El botón se **deshabilita temporalmente** para evitar duplicados.
3. El sistema envía los datos al servidor para registrar la venta.
4. Si todo es correcto:
   - Aparece una **notificación verde** de éxito: *"Venta registrada exitosamente."*
   - La notificación incluye un enlace **"📄 Ver/Imprimir Ticket"** (se abre en nueva pestaña).
   - El carrito se vacía automáticamente.
   - Los campos del formulario se limpian (cliente, mesa, pago).
5. Si hay error (ej. stock insuficiente), aparece una **notificación roja** con el detalle del problema.

#### ¿Qué pasa con el ticket PDF?
- El ticket se **genera en el momento** de la venta con los datos completos (fecha, vendedor, cliente, productos, totales, método de pago).
- Se **guarda automáticamente en el servidor** en la ruta `instance/pdfs/tickets_ventas/`.
- El nombre del archivo sigue el patrón:
  - **Para llevar:** `Llevar_[Cliente]_[Vendedor]_[Fecha].pdf`
  - **En mesa:** `[Mesa]_[Vendedor]_[Fecha].pdf`
- El ticket **NO se descarga automáticamente** al PC del cajero, evitando saturar la carpeta de descargas.
- El cajero puede **ver o imprimir el ticket** usando el enlace de la notificación de éxito.

> [!NOTE]
> La notificación de éxito con el enlace al ticket desaparece automáticamente después de **8 segundos**. Si necesitas el ticket después de ese tiempo, el Administrador puede localizarlo en el servidor en `instance/pdfs/tickets_ventas/`.

#### Posibles errores al confirmar:
| Error | Causa |
|---|---|
| "Por favor, ingrese el nombre del cliente." | El campo Nombre del Cliente está vacío |
| "El carrito está vacío." | No hay productos en la orden |
| "Seleccione un método de pago válido." | No hay método de pago seleccionado |
| "El monto recibido es menor al total." | Pago en efectivo insuficiente |
| "Stock insuficiente: [producto] (Disponible: X, Solicitado: Y)" | No hay suficiente inventario de ese producto |

---

## 4. 🛒 Monitor de Órdenes

### Acceso
- **URL:** `http://127.0.0.1:5000/ordenes`
- **Menú lateral:** 🛒 Órdenes
- **Roles:** ✅ Administrador | ✅ Vendedor

### Descripción General

Esta pantalla permite visualizar y gestionar todas las **órdenes activas** del sistema en tiempo real. Muestra las órdenes que han sido creadas y aún no han sido completadas o canceladas.

---

### 4.1 Tabla de Órdenes

La tabla principal muestra las siguientes columnas:

| Columna | Descripción |
|---|---|
| **Cliente** | Nombre del cliente de la orden |
| **Fecha** | Fecha y hora en que se registró la orden |
| **Vendedor** | Usuario que creó la orden |
| **Estado** | Estado actual de la orden (ver estados abajo) |
| **Acciones** | Botones para gestionar la orden |

#### Estados de una orden

| Estado | Descripción |
|---|---|
| 🟡 **Pendiente** | La orden fue registrada pero aún no está en preparación |
| 🔵 **En proceso** | La orden está siendo preparada |
| 🟢 **Completado** | La orden fue entregada al cliente |
| 🔴 **Cancelado** | La orden fue cancelada (con motivo registrado) |

---

### 4.2 Búsqueda y Filtros

Encima de la tabla hay herramientas de filtrado:

| Filtro | Función |
|---|---|
| **Campo de texto "Nombre del cliente"** | Filtra las órdenes en tiempo real mientras escribes |
| **Selector "Todos los vendedores"** | Filtra por el vendedor que creó la orden |
| **Botón 🔄 Reestablecer** | Limpia todos los filtros aplicados y muestra todas las órdenes |

---

### 4.3 Ver Detalles de una Orden

Al hacer clic en el botón **👁️** de una orden en la tabla, se abre un **modal de detalles** que muestra:
- Nombre del cliente
- Mesa / Tipo de servicio
- Fecha y hora
- Listado completo de productos con cantidades y precios
- Total de la orden
- Estado actual

---

### 4.4 Cambiar Estado de una Orden

Para avanzar el estado de una orden:
1. Localiza la orden en la tabla.
2. Haz clic en el botón de cambio de estado (selector o botón de acción).
3. Aparecerá un **modal de confirmación** con el mensaje del cambio a realizar.
4. Haz clic en **"Sí"** para confirmar o **"No"** para cancelar.

---

### 4.5 Cancelar una Orden ⚠️

La cancelación de una orden es una **acción crítica** que requiere confirmación y motivo obligatorio:

1. Localiza la orden en la tabla.
2. Haz clic en el botón de acción para cancelar.
3. Se abre el **modal de confirmación de cancelación** que incluye:
   - Mensaje de confirmación: *"¿Deseas cancelar esta orden?"*
   - **Campo de texto obligatorio "Motivo de cancelación"** (máximo 255 caracteres)
4. Escribe un motivo claro y descriptivo (ej: "Cliente no recogió el pedido", "Error en la orden, cliente solicitó cambio").
5. Haz clic en **"Sí"** para confirmar la cancelación.
6. La cancelación queda **registrada en el sistema de auditoría** con el motivo, usuario y fecha/hora.

> [!CAUTION]
> No es posible confirmar la cancelación si el campo de motivo está vacío. El sistema lo exige para mantener la trazabilidad. Las órdenes canceladas **no se pueden recuperar**.

---

## 5. 📜 Historial de Ventas

### Acceso
- **URL:** `http://127.0.0.1:5000/historial`
- **Menú lateral:** 📜 Historial
- **Roles:** ✅ Administrador | ✅ Vendedor

### Descripción General

Pantalla de consulta del registro completo de ventas realizadas. Por defecto muestra las ventas del **día actual**, con opciones de filtrado y exportación.

---

### 5.1 Tabla de Ventas

Columnas de la tabla principal:

| Columna | Descripción |
|---|---|
| **Vendedor** | Usuario que registró la venta |
| **Cliente** | Nombre del cliente |
| **Fecha de Venta** | Fecha y hora exacta de la venta |
| **Total** | Monto total de la venta |
| **Mesa** | Mesa asignada o "Para llevar" |
| **Acciones** | Botón para ver el detalle completo de la venta |

La tabla incluye **paginación del lado del servidor** para evitar cargar miles de registros simultáneamente. Puedes navegar entre páginas con los controles de paginación al pie de la tabla.

---

### 5.2 Filtros de Búsqueda

La barra de filtros encima de la tabla incluye:

| Filtro | Descripción |
|---|---|
| **Nombre del cliente** | Búsqueda de texto libre (máximo 30 caracteres) |
| **Todos los vendedores** | Selector para filtrar por vendedor específico |
| **Desde (fecha)** | Fecha de inicio del rango de búsqueda |
| **Hasta (fecha)** | Fecha de fin del rango de búsqueda |
| **🔄 Reestablecer** | Limpia todos los filtros |

> [!TIP]
> Para ver las ventas de un día específico, establece la misma fecha en "Desde" y "Hasta". Para ver el mes completo, pon el primer día del mes en "Desde" y el último en "Hasta".

---

### 5.3 Ver Detalle de una Venta

Al hacer clic en el botón **👁️** de una venta en la tabla, se abre un **modal de detalles** que muestra:
- Nombre del cliente y vendedor
- Fecha y hora exacta
- Mesa / tipo de servicio
- Método de pago
- Listado completo de productos comprados con cantidades, tamaños y precios unitarios
- Subtotales por ítem
- **Total de la venta**

---

### 5.4 Exportar a Excel / CSV

Haz clic en el botón **📥 Exportar a Excel** (en verde, en la barra de filtros) para descargar un archivo Excel/CSV con los resultados del filtro activo.

> [!NOTE]
> La exportación respeta los filtros activos en ese momento. Si quieres exportar solo las ventas de un vendedor o de una semana específica, aplica primero esos filtros y luego exporta.

---

### 5.5 Regla de Inmutabilidad de Ventas

> [!CAUTION]
> **Las ventas nunca se borran del sistema.** El historial es un registro fiscal, contable y legal que debe permanecer intacto. La inmutabilidad es una regla de negocio no negociable del sistema. No existe ningún botón de eliminación de ventas, ni para Administradores.

---

## 6. 🏷️ Inventario (Solo Admin)

### Acceso
- **URL:** `http://127.0.0.1:5000/inventario`
- **Menú lateral:** 🏷️ Inventario
- **Roles:** ✅ Administrador | ❌ Vendedor

### Descripción General

Módulo para controlar las existencias físicas de los productos del catálogo. Permite consultar el stock actual, configurar umbrales mínimos y máximos, y realizar ajustes manuales con trazabilidad.

---

### 6.1 Tabla de Inventario

Columnas de la tabla:

| Columna | Descripción |
|---|---|
| **Nombre** | Nombre del producto |
| **Stock** | Cantidad actual en existencias |
| **Stock Mínimo** | Umbral mínimo definido (alerta cuando se alcanza) |
| **Stock Máximo** | Umbral máximo definido (capacidad máxima de almacenamiento) |
| **Estado** | Semáforo de alerta visual del stock |
| **Acciones** | Botón ✏️ para editar el inventario del producto |

#### Estados del inventario

| Estado | Color | Condición |
|---|---|---|
| 🔴 **CRÍTICO** | Rojo | Stock ≤ Stock Mínimo, o Stock ≤ Stock Mínimo + 5 |
| 🟡 **ALERTA** | Amarillo | Stock ≤ Stock Mínimo + 10 |
| 🟢 **ACEPTABLE** | Verde | Stock > Stock Mínimo + 10 |

> [!WARNING]
> Cuando cualquier producto tiene estado CRÍTICO, el ícono de Inventario en el sidebar mostrará un **punto rojo de alerta** visible desde cualquier pantalla del sistema.

---

### 6.2 Buscador de Inventario

En la parte superior hay un campo de búsqueda:
- Escribe el nombre del producto para filtrar la tabla en tiempo real.
- El botón **🔄 Reestablecer** limpia el filtro y muestra todos los productos.

---

### 6.3 Editar Inventario de un Producto

Al hacer clic en el botón **✏️** de un producto, se abre el **modal de edición de inventario** que muestra:

**Columna "Valores Actuales" (solo lectura):**
- Stock actual
- Stock mínimo actual
- Stock máximo actual

**Columna "Nuevos Valores" (editable):**

| Campo | Descripción | Límites |
|---|---|---|
| **Ajustar Stock (+/-)** | Cantidad a sumar o restar al stock actual (ej: `10` para agregar, `-5` para restar) | -9,999 a 9,999 |
| **Nuevo Mínimo** | Nuevo valor para el stock mínimo | 0 a 999 |
| **Nuevo Máximo** | Nuevo valor para el stock máximo | 0 a 9,999 |

> [!NOTE]
> Deja en blanco los campos que no quieras modificar. Solo se actualizan los campos con valor ingresado.

#### Proceso de guardado con confirmación obligatoria:

1. Ingresa los valores que deseas modificar en la columna "Nuevos Valores".
2. Haz clic en **"Guardar Cambios"**.
3. Se abre el **modal de confirmación** con:
   - Descripción del ajuste a realizar
   - **Campo de texto obligatorio "Motivo del ajuste"** (máximo 255 caracteres)
   - Ejemplos de motivo: *"Merma por caducidad"*, *"Reabastecimiento con proveedor"*, *"Ajuste de inventario físico"*
4. Escribe el motivo.
5. Haz clic en **"Confirmar"** para aplicar el cambio, o **"Cancelar"** para descartarlo.

> [!IMPORTANT]
> **Todo ajuste de inventario queda registrado en la tabla de auditoría** con: usuario que realizó el ajuste, fecha/hora, valores anteriores, valores nuevos y motivo. Esta información es obligatoria por normativa interna.

---

## 7. 💵 Corte de Caja (Solo Admin)

### Acceso
- **URL:** `http://127.0.0.1:5000/corteCaja`
- **Menú lateral:** 💵 Corte de Caja
- **Roles:** ✅ Administrador | ❌ Vendedor

### Descripción General

Módulo para realizar el **cierre contable del período de trabajo**. Registra el resumen de ventas, compara el efectivo contado físicamente contra el calculado por el sistema, y genera el registro oficial del corte.

---

### 7.1 Historial de Cortes (Tabla Principal)

La pantalla principal muestra todos los cortes de caja realizados:

| Columna | Descripción |
|---|---|
| **Fecha de inicio** | Fecha y hora de inicio del período |
| **Fecha de cierre** | Fecha y hora de cierre del período |
| **Fondo** | Dinero base con que inició la caja |
| **Contado** | Efectivo físicamente contado al cierre |
| **Calculado** | Total de ventas en efectivo según el sistema |
| **Pagos realizados** | Salidas de dinero (pagos a proveedores u otros) |
| **Acciones** | Botón 👁️ para ver el detalle completo del corte |

---

### 7.2 Realizar un Nuevo Corte de Caja

Haz clic en el botón **"Realizar Corte"** (en la parte superior derecha de la pantalla). Se abre el **modal de Corte de Caja** con los siguientes elementos:

#### Selector de Fechas

| Campo | Comportamiento |
|---|---|
| **Desde (Fecha de inicio)** | 🔒 **BLOQUEADO automáticamente** si existe un corte previo. Se establece al cierre exacto del último corte registrado y no puede modificarse. Si es el primer corte del sistema, es editable. |
| **Hasta (Fecha de cierre)** | Editable. Por defecto se puede ingresar la fecha/hora actual hasta el momento del corte. |
| **Botón "Filtrar"** | Consulta las ventas del período seleccionado y carga los totales calculados por el sistema. |

> [!CAUTION]
> **La fecha de inicio es fija e inamovible** (cuando existe un corte previo). Esta restricción es una regla contable no negociable: garantiza que no haya "huecos" entre períodos de corte. No existe forma de cambiarla manualmente.

#### Tabla de Comparación (Contado vs Calculado)

La tabla central del modal muestra:

| Fila | Contado (manual) | Calculado (sistema) | Diferencia |
|---|---|---|---|
| **Efectivo** | 📝 Editable — ingresa el efectivo físico contado | Automático (ventas en efectivo) | Automático |
| **Transferencias** | Solo lectura | Automático (ventas por transferencia) | Automático |
| **Tarjeta** | Solo lectura | Automático (ventas con tarjeta) | Automático |
| **Total** | Solo lectura | Automático | Automático |

> [!IMPORTANT]
> Solo el campo **Efectivo Contado** es editable. Los demás se calculan automáticamente al presionar "Filtrar" (o "Calcular Corte").

#### Panel lateral del modal

| Campo | Descripción |
|---|---|
| **Fondo** | Monto inicial de la caja (efectivo con que se abrió el turno). Editable. |
| **Pagos realizados** | Suma de pagos hechos con el dinero de la caja (proveedores, gastos). Editable. |
| **Botón "Calcular Corte"** | Calcula y muestra las diferencias entre lo contado y lo calculado |
| **Botón "Realizar Corte"** | Guarda el corte de caja de forma definitiva en el sistema |

> [!WARNING]
> El botón **"Realizar Corte"** solo estará activo cuando la **diferencia en efectivo sea igual a $0**. Si hay diferencia, el sistema muestra una alerta: *"La diferencia debe ser 0 para realizar el corte."* Revisa el efectivo contado antes de confirmar.

---

### 7.3 Ver Detalle de un Corte

Al hacer clic en el botón **👁️** de cualquier corte en la tabla, se abre un modal con el detalle completo:

- ID del corte
- Fecha de inicio y cierre
- Fondo inicial
- Total contado
- Total calculado por el sistema
- Desglose: Total efectivo, Total transferencias, Total tarjeta
- Pagos realizados

---

### 7.4 Exportar Cortes a Excel / CSV

Haz clic en el botón **📥 Descargar Excel / CSV** en la parte superior de la pantalla para descargar **todos los cortes de caja** en formato Excel.

---

### 7.5 Regla de Continuidad de Cortes (Sin Huecos)

> [!CAUTION]
> El sistema garantiza la **continuidad perfecta** entre cortes de caja:
> - El **campo "Fecha Desde"** se establece automáticamente al valor exacto de `fecha_hora_cierre` del corte inmediato anterior.
> - No puede existir ningún período sin corte entre dos registros consecutivos.
> - Esta regla es una exigencia contable y fiscal que el sistema implementa a nivel técnico (campo `readonly` en la interfaz y validación en el servidor).

---

## 8. 💰 Reportes Financieros (Solo Admin)

### Acceso
- **URL:** `http://127.0.0.1:5000/reporteFinanciero`
- **Menú lateral:** 💰 Reportes de Ventas
- **Roles:** ✅ Administrador | ❌ Vendedor

### Descripción General

Vista consolidada de todos los cortes de caja realizados, con cálculo automático de **ganancia o pérdida** por período.

---

### 8.1 Tabla de Reportes

| Columna | Descripción |
|---|---|
| **Fecha** | Fecha de cierre del corte (formato: YYYY-MM-DD) |
| **Fondo** | Dinero base con que inició la caja en ese período |
| **Ventas Totales** | Suma total de todas las ventas del período (calculado por el sistema) |
| **Salidas de dinero** | Pagos realizados durante el período |
| **Ganancia/Pérdida** | Resultado neto del período *(verde = ganancia, rojo = pérdida)* |

La columna **Ganancia/Pérdida** se muestra en color verde si el valor es positivo (ganancia) o en color rojo si es negativo (pérdida), facilitando la identificación visual rápida.

---

### 8.2 Exportar Reportes

Haz clic en el botón **📥 Descargar Excel / CSV** en la parte superior para exportar el historial completo de cortes con toda la información financiera.

> [!TIP]
> Este reporte es ideal para contabilidad mensual. Exporta al final de cada mes para llevar el registro contable fuera del sistema.

---

## 9. 📝 Gestión de Productos (Solo Admin)

### Acceso
- **URL:** `http://127.0.0.1:5000/gestionProductos`
- **Menú lateral:** 📝 Gestión Productos
- **Roles:** ✅ Administrador | ❌ Vendedor

### Descripción General

Módulo para administrar el **catálogo completo de productos** del menú: agregar nuevos productos, editar los existentes, ver detalles y activar/desactivar productos.

---

### 9.1 Tabla de Productos

Columnas de la tabla:

| Columna | Descripción |
|---|---|
| **Nombre** | Nombre del producto |
| **Tamaño** | Variantes disponibles (ej: "Chico, Mediano, Grande") o "No Aplica" si es talla única |
| **Categoría** | Categoría a la que pertenece el producto |
| **Precio** | Precio base del producto |
| **Imagen** | Miniatura de la imagen del producto |
| **Acciones** | Botones: 👁️ Ver | ✏️ Editar | 🗑️ Desactivar |

---

### 9.2 Filtros de Búsqueda

La barra superior incluye:

| Filtro | Descripción |
|---|---|
| **Buscar por nombre** | Filtra en tiempo real por nombre del producto (máx. 50 caracteres) |
| **Todos los tamaños** | Filtra por tamaño/variante específica |
| **Todas las categorías** | Filtra por categoría |
| **🔄 Reestablecer** | Limpia todos los filtros |

---

### 9.3 Agregar Nuevo Producto

Haz clic en el botón **➕ Agregar Producto** en la parte superior. Se abre el modal con el formulario:

**Sección izquierda del formulario:**

| Campo | Descripción | Restricciones |
|---|---|---|
| **Nombre** | Nombre del producto | Obligatorio, máx. 50 caracteres |
| **Descripción** | Descripción corta del producto | Opcional, máx. 100 caracteres |
| **Tamaño** | Variante de tamaño (selector) | Obligatorio |
| **Precio** | Precio del producto | Obligatorio, 0-999, solo enteros |
| **Stock** | Cantidad inicial en existencias | Obligatorio, 0-999 |

**Sección derecha del formulario:**

| Campo | Descripción | Restricciones |
|---|---|---|
| **Stock Mínimo** | Umbral de alerta de stock bajo | Obligatorio, 0-999 |
| **Stock Máximo** | Capacidad máxima de almacenamiento | Obligatorio, 0-999 |
| **Categoría** | Categoría del producto (selector) | Obligatorio |
| **Imagen del Producto** | Foto del producto | Obligatorio, formatos: PNG, JPG, WEBP |

#### Subir imagen del producto

El área de imagen ofrece dos métodos:

**Método 1 — Arrastrar y soltar (Drag & Drop):**
1. Abre el explorador de archivos de tu PC.
2. Selecciona la imagen del producto.
3. **Arrástrate** al área de carga marcada con el ícono de nube ☁️.
4. Suelta el archivo sobre el área.

**Método 2 — Clic para examinar:**
1. Haz clic directamente en el área de carga (o en el botón "Subir imagen").
2. Se abre el explorador de archivos.
3. Navega y selecciona la imagen.
4. Haz clic en "Abrir".

**Preview de imagen:**
Una vez seleccionada la imagen (por cualquier método):
- Aparece una **vista previa (thumbnail)** de la imagen seleccionada.
- Se muestra el nombre del archivo.
- Aparece un botón **"Cambiar foto"** para reemplazarla si es necesario.

> [!TIP]
> Usa imágenes de buena calidad y fondo claro para que los productos se vean atractivos en el menú. Formatos aceptados: **PNG, JPG, WEBP**.

Una vez llenos todos los campos, haz clic en **"Guardar"** para agregar el producto al catálogo.

---

### 9.4 Ver Producto

Al hacer clic en el botón **👁️** de un producto en la tabla, se abre un **modal de solo lectura** con toda la información del producto:
- Imagen, nombre y categoría (en el encabezado)
- ID del producto
- Precio
- Descripción
- Tamaño(s)
- Stock actual
- Stock Mínimo
- Stock Máximo

---

### 9.5 Editar Producto

Al hacer clic en el botón **✏️** de un producto, se abre el mismo modal de formulario pero **pre-cargado** con los datos actuales del producto.

- Modifica los campos que necesites.
- Para cambiar la imagen, haz clic en **"Cambiar foto"** o arrastra la nueva imagen al área de carga.
- Haz clic en **"Guardar"** para confirmar los cambios.

---

### 9.6 Desactivar / Activar Producto

Al hacer clic en el botón **🗑️** de un producto:
1. Se abre un **modal de confirmación**: *"¿Deseas eliminar este producto?"*
2. Haz clic en **"Sí"** para desactivar el producto o **"No"** para cancelar.

> [!IMPORTANT]
> Los productos **nunca se eliminan permanentemente** de la base de datos. Al "eliminar" un producto, este se **desactiva** y deja de aparecer en el Menú de Ventas y en los filtros activos. Un Administrador puede reactivarlo cuando sea necesario.

---

## 10. 🤝 Gestión de Usuarios (Solo Admin)

### Acceso
- **URL:** `http://127.0.0.1:5000/gestionUsuarios`
- **Menú lateral:** 🤝 Gestión Usuarios
- **Roles:** ✅ Administrador | ❌ Vendedor

### Descripción General

Módulo para administrar las cuentas de acceso al sistema: crear nuevos usuarios, consultar información, editar datos, activar y desactivar cuentas.

---

### 10.1 Pestañas: Usuarios Activos / Inactivos

La pantalla principal tiene dos pestañas:

| Pestaña | Descripción |
|---|---|
| **Usuarios Activos** (por defecto) | Muestra todos los usuarios que pueden iniciar sesión |
| **Usuarios Inactivos** | Muestra usuarios desactivados que no pueden iniciar sesión |

---

### 10.2 Tabla de Usuarios Activos

Columnas:

| Columna | Descripción |
|---|---|
| **Usuario** | Nombre del usuario |
| **Correo** | Correo electrónico de la cuenta |
| **Rol** | Administrador o Vendedor |
| **Fecha de Registro** | Fecha y hora en que se creó la cuenta |
| **Acciones** | 👁️ Ver | ✏️ Editar | 🗑️ Desactivar |

---

### 10.3 Tabla de Usuarios Inactivos

Columnas:

| Columna | Descripción |
|---|---|
| **Usuario** | Nombre del usuario |
| **Correo** | Correo electrónico |
| **Rol** | Rol asignado |
| **Fecha de Desactivación** | Fecha/hora en que se desactivó |
| **Acciones** | 👁️ Ver | ✅ Activar |

---

### 10.4 Filtros de Búsqueda

La barra de filtros incluye:

| Filtro | Descripción |
|---|---|
| **Buscar por nombre** | Búsqueda de texto (máx. 30 caracteres) |
| **Desde (fecha)** | Filtra usuarios registrados desde esta fecha |
| **Hasta (fecha)** | Filtra usuarios registrados hasta esta fecha |
| **🔄 Reestablecer** | Limpia todos los filtros |

---

### 10.5 Crear Nuevo Usuario

Haz clic en el botón **➕ Agregar Usuario**. Se abre el modal con el formulario:

**Sección izquierda:**

| Campo | Descripción | Restricciones |
|---|---|---|
| **Nombre de Usuario** | Nombre completo o alias del usuario | Obligatorio, máx. 100 caracteres |
| **Correo** | Email de la cuenta (usado para recuperación de contraseña) | Obligatorio, formato email válido, máx. 100 caracteres |

**Sección derecha:**

| Campo | Descripción | Restricciones |
|---|---|---|
| **Contraseña** | Contraseña inicial del nuevo usuario | Obligatorio, mín. 8 caracteres, debe incluir letras + números + al menos un símbolo |
| **Tipo de Privilegio** | Rol del usuario (selector) | Obligatorio: Administrador o Vendedor |

> [!TIP]
> El campo de contraseña tiene un botón 👁️ para mostrar u ocultar el texto mientras lo escribes.

Una vez completado el formulario, haz clic en **"💾 Guardar"** para crear el usuario.

---

### 10.6 Ver Detalles de un Usuario

Al hacer clic en el botón **👁️** de un usuario, se abre un modal con:
- Avatar con la inicial del nombre
- Nombre completo del usuario
- Rol asignado
- ID del sistema
- Correo electrónico
- Fecha de registro

---

### 10.7 Editar Usuario

Al hacer clic en el botón **✏️** de un usuario activo, se abre el modal de formulario pre-cargado con los datos actuales.

- Modifica los campos necesarios (nombre, correo, rol).
- Si necesitas **cambiar la contraseña**, escribe la nueva en el campo correspondiente.
- Haz clic en **"💾 Guardar"** para confirmar los cambios.

> [!NOTE]
> Si dejas el campo de contraseña en blanco al editar un usuario, la contraseña actual **no se modifica**.

---

### 10.8 Desactivar Usuario

Al hacer clic en el botón **🗑️** de un usuario activo:
1. Aparece el **modal de confirmación**: *"¿Estás seguro de que deseas eliminar este usuario?"*
2. Haz clic en **"Sí"** para desactivar o **"No"** para cancelar.
3. El usuario desaparece de la pestaña "Usuarios Activos" y pasa a "Usuarios Inactivos".

> [!CAUTION]
> Los usuarios **nunca se eliminan permanentemente**. Al "eliminar" un usuario, su cuenta queda desactivada. El usuario no podrá iniciar sesión hasta que un Administrador lo reactive.

---

### 10.9 Reactivar Usuario

Desde la pestaña **"Usuarios Inactivos"**:
1. Localiza el usuario a reactivar.
2. Haz clic en el botón **"✅ Activar"**.
3. Aparece el modal de confirmación: *"¿Estás seguro de que deseas activar este usuario?"*
4. Haz clic en **"Sí, Activar"**.
5. El usuario vuelve a aparecer en "Usuarios Activos" y puede iniciar sesión nuevamente.

---

## 11. 🌙 Procedimiento de Cierre del Día

Al finalizar el turno o el día laboral, el **Administrador** debe seguir este procedimiento en orden para cerrar correctamente el sistema:

---

### Paso 1 — Verificar que no haya Órdenes Pendientes

1. Ir a **🛒 Órdenes** en el menú lateral.
2. Revisar que no quede ninguna orden en estado **"Pendiente"** o **"En proceso"**.
3. Si quedan órdenes sin concluir:
   - Si se pueden completar, cambiarlas a estado **"Completado"**.
   - Si no se pueden completar (cliente ya no espera, error, etc.), **cancelarlas** con el motivo correspondiente (campo obligatorio).

> [!IMPORTANT]
> Al finalizar el día **no deben quedar órdenes en estado Pendiente o En proceso**. Toda orden no concluida debe cancelarse con su motivo registrado.

---

### Paso 2 — Realizar el Corte de Caja

1. Ir a **💵 Corte de Caja** en el menú lateral.
2. Haz clic en **"Realizar Corte"**.
3. Verifica que el campo **"Desde"** muestra la fecha/hora del último corte (bloqueado).
4. En el campo **"Hasta"**, ingresa la fecha y hora actual.
5. Haz clic en **"Filtrar"** para cargar los totales del sistema.
6. Cuenta físicamente el efectivo en la caja.
7. Ingresa el monto contado en el campo **"Efectivo Contado"**.
8. Ingresa el **Fondo** (dinero base de la caja) y los **Pagos realizados** del día.
9. Haz clic en **"Calcular Corte"** para ver las diferencias.
10. Si la diferencia es **$0**, haz clic en **"Realizar Corte"** para guardar.
11. Si hay diferencia, revisa el conteo físico del efectivo.

---

### Paso 3 — Descargar el Reporte (si se requiere)

1. Desde la pantalla de **Corte de Caja** o **Reportes Financieros**.
2. Haz clic en **"📥 Descargar Excel / CSV"**.
3. El archivo se descargará automáticamente en la carpeta de Descargas del navegador.

---

### Paso 4 — Cerrar Sesión

1. En el menú lateral, haz clic en **🚪 Salir**.
2. El sistema te redirigirá a la pantalla de confirmación de cierre de sesión.
3. Confirma la salida.
4. Cierra el navegador.

> [!TIP]
> Es buena práctica cerrar sesión correctamente en lugar de simplemente cerrar el navegador, especialmente en equipos compartidos.

---

## 12. ❓ Preguntas Frecuentes / Solución de Problemas

---

### ❓ ¿Qué hago si olvidé mi contraseña?

**Solución:**
1. En la pantalla de Login, haz clic en **"¿Olvidaste tu contraseña?"**.
2. Ingresa el correo electrónico de tu cuenta.
3. Revisa tu bandeja de entrada (y la carpeta de Spam) por un correo con el código de verificación.
4. Ingresa el código en el sistema.
5. Establece una nueva contraseña (mínimo 8 caracteres, con letras, números y un símbolo).

Si el problema persiste o no tienes acceso al correo registrado, **contacta al Administrador del sistema** para que restablezca tu contraseña manualmente.

---

### ❓ ¿Por qué no puedo cambiar la fecha de inicio del corte de caja?

**Respuesta:**
El campo **"Fecha Desde"** está **bloqueado por diseño**. Se establece automáticamente con la fecha y hora exacta del cierre del corte anterior.

Esto garantiza la **continuidad perfecta** entre cortes de caja: no puede existir ningún período de tiempo sin cobertura entre dos cortes. Esta es una exigencia contable y fiscal que el sistema implementa automáticamente.

> [!NOTE]
> Si es el **primer corte** que se realiza en el sistema (no existe ningún corte previo), el campo "Fecha Desde" sí será editable para que puedas establecer la fecha de inicio del primer período.

---

### ❓ ¿Dónde están los tickets PDF de las ventas?

**Respuesta:**
Los tickets PDF se guardan automáticamente en el servidor en la carpeta:

```
instance/pdfs/tickets_ventas/
```

El nombre del archivo sigue el patrón:
- **Para llevar:** `Llevar_[NombreCliente]_[NombreVendedor]_[Fecha].pdf`
- **En mesa:** `[Mesa]_[NombreVendedor]_[Fecha].pdf`

**Para ver un ticket inmediatamente después de la venta:**
Cuando aparece la notificación de éxito *"Venta registrada exitosamente."*, haz clic en el enlace **"📄 Ver/Imprimir Ticket"** (se abre en nueva pestaña). Esta opción está disponible durante los 8 segundos que dura la notificación.

> [!NOTE]
> Los tickets **no se descargan automáticamente** al equipo del cajero, esto es intencional para no saturar la carpeta de Descargas. Para acceder a un ticket antiguo, el Administrador debe buscarlo en la carpeta del servidor.

---

### ❓ ¿Se pueden borrar ventas del historial?

**Respuesta: NO.**

Las ventas son registros **fiscales, contables y legales inmutables**. El sistema no tiene ninguna función para borrar ventas, ni para Administradores. Esta es una regla de negocio no negociable que protege la integridad del historial financiero del negocio.

Si una venta fue registrada con error, el procedimiento correcto es:
1. Ir a **🛒 Órdenes** y cancelar la orden correspondiente con un motivo descriptivo.
2. La venta permanecerá en el historial, pero quedará marcada como cancelada con su motivo registrado en auditoría.

---

### ❓ ¿Qué pasa si cierro el navegador a mitad de una venta?

**Respuesta:**
Si cierras el navegador **antes de hacer clic en "Realizar la orden"**, la venta **no se registra** en el sistema. El carrito solo existe en memoria del navegador (sesión de la pestaña actual) y se pierde al cerrar.

**Recomendación:**
- Nunca cierres el navegador si tienes una orden en proceso.
- Si el navegador se cierra accidentalmente, vuelve a ingresar al sistema y registra la venta nuevamente.
- Si el cliente ya pagó, verifica primero en el Historial de Ventas que la venta no haya quedado registrada antes de crear una nueva.

---

### ❓ ¿Por qué no veo las opciones de Inventario, Corte de Caja, Gestión de Productos o Gestión de Usuarios?

**Respuesta:**
Estas secciones son **exclusivas del rol Administrador**. Si tu cuenta tiene el rol **Vendedor**, estas opciones no aparecen en el menú lateral y no puedes acceder a ellas.

Contacta al Administrador si necesitas permisos adicionales o si crees que tu rol es incorrecto.

---

### ❓ ¿El sistema funciona sin internet?

**Respuesta:**
Sí, siempre que el servidor esté ejecutándose en la red local. El sistema POS opera en la red interna del negocio (`http://127.0.0.1:5000` o la IP del servidor).

Sin embargo, las funciones que requieren internet son:
- Recuperación de contraseña por correo electrónico (requiere acceso a internet para enviar el email)
- Sincronización con la base de datos en la nube Aiven (si está configurada)

---

### ❓ ¿Qué significa el punto rojo que aparece junto a "Inventario" en el menú?

**Respuesta:**
El punto rojo `●` es una **alerta visual de stock crítico**. Indica que al menos un producto tiene existencias en estado **CRÍTICO** (igual o por debajo del stock mínimo, o hasta 5 unidades sobre el mínimo).

**Acción recomendada:**
1. Ve a **🏷️ Inventario** inmediatamente.
2. Identifica los productos en estado rojo (CRÍTICO).
3. Realiza el ajuste de stock correspondiente con el motivo del reabastecimiento.

---

### ❓ ¿Qué pasa si agrego el mismo producto dos veces al carrito?

**Respuesta:**
El sistema detecta automáticamente si el mismo producto (con el mismo tamaño/variante) ya está en el carrito y **aumenta la cantidad en 1** en lugar de agregar un ítem duplicado.

Si necesitas cantidades específicas, puedes:
1. Seguir haciendo clic en "Añadir a la orden" para incrementar de uno en uno.
2. O editar directamente el campo de cantidad en el ítem del carrito.

---

*📄 Este manual fue generado automáticamente a partir del código fuente del sistema Coffee Hacienda POS.*
*📅 Última actualización: Noviembre 2026*
*☕ Coffee Hacienda — Haciendas de San Vicente, 63737 San Vicente, Nay.*
