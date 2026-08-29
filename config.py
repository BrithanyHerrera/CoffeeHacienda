"""Configuración por entorno para Coffee Hacienda."""
import os


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH_MB', '8')) * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_VALIDATION_INTERVAL_SECONDS = int(
        os.getenv('SESSION_VALIDATION_INTERVAL_SECONDS', '60')
    )
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'testing-only-secret-key')


class ProductionConfig(BaseConfig):
    SESSION_COOKIE_SECURE = True


CONFIG_BY_ENV = {
    'LOCAL': DevelopmentConfig,
    'DEVELOPMENT': DevelopmentConfig,
    'TESTING': TestingConfig,
    'NUBE': ProductionConfig,
    'PRODUCTION': ProductionConfig,
}


def config_for_environment(app_env):
    """Obtiene la configuración correspondiente y rechaza entornos desconocidos."""
    try:
        return CONFIG_BY_ENV[app_env.upper()]
    except (AttributeError, KeyError) as error:
        raise RuntimeError(f'APP_ENV no válido: {app_env!r}') from error
