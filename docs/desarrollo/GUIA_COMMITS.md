# Guía de Convenciones para Commits (Conventional Commits)

Este documento establece el estándar Conventional Commits para el repositorio. Todo mensaje de commit debe seguir esta estructura para facilitar el análisis del historial y la automatización de versiones.

## Estructura del Commit

```text
tipo: descripción corta e imperativa

[opcional: cuerpo del mensaje explicando el contexto técnico y el motivo del cambio]
```

## Tipos de Commits Permitidos

### Cambios Funcionales
- **`feat:`** (Feature) Introducción de una nueva funcionalidad en el código.
  *Ejemplo: `feat: agregar exportación de cortes de caja en formato PDF`*
- **`fix:`** (Fix) Corrección de un error o vulnerabilidad en el sistema.
  *Ejemplo: `fix: corregir validación de stock negativo en el procesamiento de ventas`*

### Mantenimiento y Refactorización
- **`refactor:`** Reestructuración del código fuente sin alterar su comportamiento externo ni agregar funcionalidades.
  *Ejemplo: `refactor: extraer lógica de conexión a base de datos al módulo bd.py`*
- **`perf:`** (Performance) Modificaciones orientadas exclusivamente a optimizar el rendimiento.
  *Ejemplo: `perf: indexar columna fecha_hora en tventas para acelerar consultas históricas`*
- **`style:`** Ajustes de formato o estilo que no afectan la lógica del programa (espacios, indentación, o CSS estructural).
  *Ejemplo: `style: aplicar formato PEP-8 en modelos de inventario`*

### Configuración e Infraestructura
- **`docs:`** (Documentation) Modificaciones exclusivas a la documentación del proyecto (README, guías, comentarios en código).
  *Ejemplo: `docs: actualizar diagrama arquitectónico en README.md`*
- **`test:`** Incorporación o corrección de pruebas unitarias o de integración.
  *Ejemplo: `test: agregar cobertura para el módulo de cálculo de impuestos`*
- **`chore:`** Actualización de dependencias, scripts de construcción o herramientas externas.
  *Ejemplo: `chore: actualizar Flask a versión 3.1.3 en requirements.txt`*
- **`ci:`** (Continuous Integration) Cambios en la configuración de integración o despliegue continuo.

## Ejemplos de Implementación

**Incorrecto:** `se arregló el login`
**Correcto:** `fix: validar el hash de la contraseña en la autenticación de usuarios`

**Incorrecto:** `nuevos cambios en bd`
**Correcto:** `feat: agregar columna estado_pago a la tabla de devoluciones`

## Uso en Terminal

```bash
git commit -m "fix: corregir cálculo del cambio en transacciones en efectivo"
```

Para commits con contexto adicional:

```bash
git commit -m "feat: implementar caché de alertas de inventario

Se integra Redis para almacenar los conteos de inventario durante 120
segundos, reduciendo la carga sobre MySQL en un 40% durante horas pico."
```
