# Pool de conexiones MySQL (local y nube)
import os
import logging
import pymysql
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, 'bd.env'))

_pool = None

def _crear_pool():
    """Crea el pool con la interfaz DB_* y compatibilidad con nombres heredados."""
    global _pool
    
    env = os.getenv('APP_ENV', 'LOCAL').upper()
    legacy_suffix = 'CLOUD' if env in {'NUBE', 'PRODUCTION'} else 'LOCAL'

    def database_setting(name, legacy_name, default=None):
        return os.getenv(name) or os.getenv(f'{legacy_name}_{legacy_suffix}', default)

    host = database_setting('DB_HOST', 'DB_HOST')
    user = database_setting('DB_USER', 'DB_USER')
    password = database_setting('DB_PASSWORD', 'DB_PASS')
    database = database_setting('DB_NAME', 'DB_NAME')
    port = int(database_setting('DB_PORT', 'DB_PORT', '3306'))

    if not all((host, user, password, database)):
        raise RuntimeError('La configuración de base de datos está incompleta')

    if env in {'NUBE', 'PRODUCTION'}:
        ssl_ca = os.getenv('DB_SSL_CA')
        if not ssl_ca:
            raise RuntimeError('DB_SSL_CA es obligatorio para verificar la conexión TLS con Aiven')
        if not os.path.isfile(ssl_ca):
            raise RuntimeError('DB_SSL_CA no apunta a un certificado CA existente')
    else:
        ssl_ca = None

    # En nube no pre-creamos conexiones SSL (lentas); en local sí para más agilidad
    mincached = 0 if env in {'NUBE', 'PRODUCTION'} else 2

    pool_kwargs = dict(
        creator=pymysql,
        maxconnections=10,
        mincached=mincached,
        maxcached=5,
        maxshared=0,
        blocking=True,
        maxusage=None,
        setsession=[],
        ping=4,
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
    )
    
    if ssl_ca:
        pool_kwargs.update(
            ssl_ca=ssl_ca,
            ssl_verify_cert=True,
            ssl_verify_identity=True,
        )
    
    _pool = PooledDB(**pool_kwargs)
    logger.info(f"Pool creado para {env} (mincached={mincached})")

def Conexion_BD():
    """Devuelve una conexión del pool. Al hacer conn.close() regresa al pool."""
    global _pool
    if _pool is None:
        _crear_pool()
    return _pool.connection()
