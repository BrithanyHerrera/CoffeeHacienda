from models import modelsLimpieza


def test_limpieza_validaciones_expiradas_tolera_bd_no_disponible(monkeypatch):
    def unavailable_database():
        raise ConnectionError('database unavailable')

    monkeypatch.setattr(modelsLimpieza, 'Conexion_BD', unavailable_database)

    assert modelsLimpieza.limpiar_validaciones_expiradas() == 0


def test_limpieza_recuperaciones_expiradas_tolera_bd_no_disponible(monkeypatch):
    def unavailable_database():
        raise ConnectionError('database unavailable')

    monkeypatch.setattr(modelsLimpieza, 'Conexion_BD', unavailable_database)

    assert modelsLimpieza.limpiar_codigos_recuperacion_expirados() == 0
