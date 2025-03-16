import pymysql
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

def Conexion_BD():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3307)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root'),
            database=os.getenv('DB_NAME', 'bd'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Conexión exitosa")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error de conexión: {e}")
        raise
