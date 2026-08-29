# Operación segura con Aiven

Este documento describe los pasos que requieren acceso humano al servicio. El
código no ejecuta migraciones automáticamente al iniciar la aplicación.

## Antes de publicar una versión

- Confirmar que `APP_ENV=NUBE` y que `DB_SSL_CA` apunta al certificado oficial.
- Usar una cuenta de aplicación con permisos de lectura/escritura sobre el
  esquema, sin privilegios administrativos del servicio.
- Configurar `RATELIMIT_STORAGE_URI` con Redis compartido si existen varias
  instancias web.
- Rotar cualquier contraseña o secreto que haya aparecido en `bd.sql` o en el
  historial del repositorio. Eliminarlo del archivo actual no invalida el dato
  que ya fue expuesto.

## Respaldo y migración

1. Programar una ventana sin escrituras y detener la aplicación.
2. Confirmar que el respaldo automático más reciente terminó correctamente.
3. Crear un respaldo manual adicional o una copia lógica cifrada fuera del
   repositorio.
4. Ejecutar `python scripts/apply_migrations.py --dry-run`.
5. Revisar que solo aparezcan las versiones esperadas.
6. Ejecutar `python scripts/apply_migrations.py`.
7. Ejecutar de nuevo `--dry-run`; debe responder que no hay pendientes.
8. Desplegar exactamente el commit asociado a esas migraciones.

## Prueba de humo

- `GET /health` devuelve `200` y `{"status":"ok"}`.
- Un administrador puede iniciar sesión.
- Un vendedor no puede abrir APIs administrativas.
- Crear una venta de prueba, completar su orden y comprobar su método de pago.
- Cancelar otra venta indicando un motivo y comprobar una sola reposición de
  inventario.
- Generar un corte sobre un rango pequeño y verificar sus tres métodos.
- Revisar logs de aplicación y conexiones ocupadas.

## Reversión

Las migraciones 002 y 003 agregan auditoría y cambian nombres/tipos de columnas.
No se deben revertir eliminando columnas con datos. Si falla la publicación:

1. Mantener la aplicación detenida.
2. Restaurar el respaldo previo en una base separada.
3. Validar conteos de usuarios, ventas, detalles y movimientos.
4. Cambiar la aplicación a la base restaurada o restaurar el servicio según el
   procedimiento de Aiven.
5. Volver al commit anterior solo junto con su esquema compatible.

La reescritura del historial Git para retirar secretos debe coordinarse con
todas las personas que tengan clones. Es una operación destructiva y separada
del despliegue normal.
