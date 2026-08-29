from models import modelsLimpieza


def test_expired_validation_cleanup_tolerates_unavailable_database(monkeypatch):
    def unavailable_database():
        raise ConnectionError('database unavailable')

    monkeypatch.setattr(modelsLimpieza, 'Conexion_BD', unavailable_database)

    assert modelsLimpieza.limpiar_validaciones_expiradas() == 0


def test_expired_recovery_cleanup_tolerates_unavailable_database(monkeypatch):
    def unavailable_database():
        raise ConnectionError('database unavailable')

    monkeypatch.setattr(modelsLimpieza, 'Conexion_BD', unavailable_database)

    assert modelsLimpieza.limpiar_codigos_recuperacion_expirados() == 0
