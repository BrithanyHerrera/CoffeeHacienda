"""Crea un administrador sin almacenar contraseñas en archivos o argumentos."""
import argparse
import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from werkzeug.security import generate_password_hash  # noqa: E402

from bd import Conexion_BD  # noqa: E402
from utils import validar_fortaleza_contrasena  # noqa: E402


def create_admin(username, email):
    password = getpass.getpass('Contraseña nueva: ')
    confirmation = getpass.getpass('Confirmar contraseña: ')
    if password != confirmation:
        raise ValueError('Las contraseñas no coinciden')
    valid, message = validar_fortaleza_contrasena(password)
    if not valid:
        raise ValueError(message)

    connection = Conexion_BD()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id FROM troles WHERE rol = 'Administrador'")
            role = cursor.fetchone()
            if not role:
                raise RuntimeError('No existe el rol Administrador')
            cursor.execute("""
                INSERT INTO tusuarios (usuario, contrasena, correo, rol_id, activo)
                VALUES (%s, %s, %s, %s, 1)
            """, (
                username.strip(), generate_password_hash(password),
                email.strip().lower(), role['Id'],
            ))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', required=True)
    parser.add_argument('--email', required=True)
    args = parser.parse_args()
    create_admin(args.username, args.email)
    print('Administrador creado correctamente.')


if __name__ == '__main__':
    main()
