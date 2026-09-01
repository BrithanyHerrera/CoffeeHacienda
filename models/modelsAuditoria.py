"""Persistencia de eventos de auditoría.

Este módulo concentra el SQL de auditoría para que las operaciones de negocio
no tengan que conocer la estructura de la tabla ``tauditoria``.
"""
import json
import logging

logger = logging.getLogger(__name__)


def registrar_evento(cursor, accion, entidad, entidad_id=None, usuario_id=None,
                     detalles=None):
    """Registra un evento en la transacción activa.

    No se almacenan contraseñas, códigos de recuperación ni otros secretos;
    ``detalles`` está pensado únicamente para metadatos operativos.
    """
    if detalles is None:
        detalles_json = None
    else:
        detalles_json = json.dumps(detalles, ensure_ascii=False, default=str)

    try:
        cursor.execute(
            """
            INSERT INTO tauditoria
                (usuario_id, accion, entidad, entidad_id, detalles)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, str(accion)[:80], str(entidad)[:80], entidad_id, detalles_json),
        )
    except Exception as error:
        # Permite arrancar una versión anterior mientras se aplica 004; todos
        # los demás errores sí deben abortar la transacción para no ocultarlos.
        if getattr(error, 'args', (None,))[0] == 1146:
            logger.warning('La tabla tauditoria aún no existe; evento omitido')
            return False
        raise
    return True
