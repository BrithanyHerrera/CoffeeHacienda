import os
import pymysql
from dotenv import load_dotenv

load_dotenv('bd.env') 

def Conexion_BD():
    # Detectar el ambiente
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

    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            ssl=ssl_config
        )
        print(f"Conexión exitosa a {env}")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error de conexión en {env}: {e}")
        raise