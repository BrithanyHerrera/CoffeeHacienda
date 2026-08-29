"""Configuración por entorno para Coffee Hacienda."""
import os


class BaseConfig:
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_TIME_LIMIT = 3600
    DEBUG = False
    TESTING = False

    @classmethod
    def as_mapping(cls):
        """Lee las variables al crear la app, después de cargar ``bd.env``."""
        return {
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'MAX_CONTENT_LENGTH': (
                int(os.getenv('MAX_CONTENT_LENGTH_MB', '8')) * 1024 * 1024
            ),
            'SESSION_COOKIE_HTTPONLY': cls.SESSION_COOKIE_HTTPONLY,
            'SESSION_COOKIE_SAMESITE': cls.SESSION_COOKIE_SAMESITE,
            'SESSION_COOKIE_SECURE': cls.SESSION_COOKIE_SECURE,
            'WTF_CSRF_TIME_LIMIT': cls.WTF_CSRF_TIME_LIMIT,
            'SESSION_VALIDATION_INTERVAL_SECONDS': int(
                os.getenv('SESSION_VALIDATION_INTERVAL_SECONDS', '60')
            ),
            'RATELIMIT_STORAGE_URI': os.getenv('RATELIMIT_STORAGE_URI', 'memory://'),
            'DEBUG': cls.DEBUG,
            'TESTING': cls.TESTING,
        }


class DevelopmentConfig(BaseConfig):
    @classmethod
    def as_mapping(cls):
        mapping = super().as_mapping()
        mapping['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        return mapping


class TestingConfig(BaseConfig):
    TESTING = True

    @classmethod
    def as_mapping(cls):
        mapping = super().as_mapping()
        mapping.update(
            WTF_CSRF_ENABLED=False,
            SECRET_KEY=os.getenv('SECRET_KEY') or 'testing-only-secret-key',
        )
        return mapping


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
        return CONFIG_BY_ENV[app_env.upper()].as_mapping()
    except (AttributeError, KeyError) as error:
        raise RuntimeError(f'APP_ENV no válido: {app_env!r}') from error
