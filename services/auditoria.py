"""Servicio de auditoría y resolución del actor de la sesión."""
from flask import has_request_context, session

from models.modelsAuditoria import registrar_evento as _persistir_evento


def usuario_actual_id():
    """Obtiene el usuario autenticado sin acoplar las rutas a los modelos."""
    if not has_request_context():
        return None
    valor = session.get('usuario_id')
    return valor if isinstance(valor, int) and valor > 0 else None


def registrar_evento(cursor, accion, entidad, entidad_id=None, usuario_id=None,
                     detalles=None):
    """Coordina el registro de auditoría dentro de la transacción actual."""
    actor = usuario_id if usuario_id is not None else usuario_actual_id()
    _persistir_evento(cursor, accion, entidad, entidad_id, actor, detalles)
