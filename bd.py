import os
import pymysql
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

load_dotenv('bd.env') 

# Variable global para el pool de conexiones
_pool = None

def _crear_pool():
    """Crea el pool de conexiones según el ambiente configurado."""
    global _pool
    
    env = os.getenv('APP_ENV', 'LOCAL')
    
    if env == 'NUBE':
        host = os.getenv('DB_HOST_CLOUD')
        user = os.getenv('DB_USER_CLOUD')
        password = os.getenv('DB_PASS_CLOUD')
        database = os.getenv('DB_NAME_CLOUD')
        port = int(os.getenv('DB_PORT_CLOUD'))
        ssl_config = {'ssl': {}}  # Obligatorio para Aiven
    else:
        host = os.getenv('DB_HOST_LOCAL')
        user = os.getenv('DB_USER_LOCAL')
        password = os.getenv('DB_PASS_LOCAL')
        database = os.getenv('DB_NAME_LOCAL')
        port = int(os.getenv('DB_PORT_LOCAL', 3307))
        ssl_config = None

    # En nube (Aiven) no pre-crear conexiones SSL al arrancar (son lentas y costosas)
    # En local las pre-creamos para una experiencia de dev más rápida
    mincached = 0 if env == 'NUBE' else 2

    pool_kwargs = dict(
        creator=pymysql,
        maxconnections=10,      # Máximo de conexiones en el pool
        mincached=mincached,    # 0 en nube = conexiones solo al ser necesarias
        maxcached=5,            # Conexiones máximas en cache (idle)
        maxshared=0,            # 0 = todas las conexiones son dedicadas
        blocking=True,          # Esperar si no hay conexión disponible
        maxusage=None,          # Reusar conexión sin límite de usos
        setsession=[],          # Comandos SQL al iniciar sesión
        ping=4,                 # Verificar conexión solo en cursor.execute()
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
    print(f"Pool de conexiones creado para {env} (mincached={mincached}, max={10})")

def Conexion_BD():
    """
    Obtiene una conexión del pool.
    Cuando se llame conn.close(), la conexión regresa al pool
    en lugar de cerrarse realmente.
    """
    global _pool
    
    if _pool is None:
        _crear_pool()
    
    return _pool.connection()