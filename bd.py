# Pool de conexiones a MySQL — soporta entorno local y Aiven (nube)
import os
import logging
import pymysql
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

logger = logging.getLogger(__name__)

load_dotenv('bd.env') 

_pool = None

def _crear_pool():
    """Crea el pool según APP_ENV (LOCAL o NUBE)."""
    global _pool
    
    env = os.getenv('APP_ENV', 'LOCAL')
    
    if env == 'NUBE':
        host = os.getenv('DB_HOST_CLOUD')
        user = os.getenv('DB_USER_CLOUD')
        password = os.getenv('DB_PASS_CLOUD')
        database = os.getenv('DB_NAME_CLOUD')
        port = int(os.getenv('DB_PORT_CLOUD'))
        ssl_config = {'ssl': {}}
    else:
        host = os.getenv('DB_HOST_LOCAL')
        user = os.getenv('DB_USER_LOCAL')
        password = os.getenv('DB_PASS_LOCAL')
        database = os.getenv('DB_NAME_LOCAL')
        port = int(os.getenv('DB_PORT_LOCAL', 3307))
        ssl_config = None

    # En nube no pre-creamos conexiones SSL (lentas); en local sí para más agilidad
    mincached = 0 if env == 'NUBE' else 2

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
    )
    
    if ssl_config:
        pool_kwargs['ssl'] = ssl_config
    
    _pool = PooledDB(**pool_kwargs)
    logger.info(f"Pool creado para {env} (mincached={mincached})")

def Conexion_BD():
    """Devuelve una conexión del pool. Al hacer conn.close() regresa al pool."""
    global _pool
    if _pool is None:
        _crear_pool()
    return _pool.connection()