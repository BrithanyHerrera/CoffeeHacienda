CLONAR REPOSITORIO A LAPTOP: :

    1. Ir a la direccion en la que quieres que se encuentre el repositorio.
    2. Clocar en el cmd: git clone https://github.com/AnaGC10/veterinariaPPI2.git

ANTES DE TIRAR CODIGO, PONER LO SIGUIENTE:

    1. git pull 

COMANDOS PARA SUBIR CAMBIOS A GITHUB:

    1. git add .
    2. git commit -m "Cualquier comentario que quieras hacer"
    3. git pull
    4. git push

COMANDO PARA INSTALAR EL ENTORNO VIRTUAL:

    1. pip install pipenv

COMANDOS PARA INSTALAR DEPENDENCIAS:

    1. pipenv install
    2. pipenv shell

COMANDO PARA ACTIVAR EL ENTORNO VIRTUAL:

    1. pipenv shell

SI QUIEREN SABER PARA QUE FUNCIONAN EXACTAMENTE:

    1. Buscar en su buscador de su agrado
    2. Preguntarle a chatgpt

COMANDO PARA VER QUIEN HA HECHO MÁS COMMITS (PONGANSE A CHAMBEAR)

    1. git shortlog -s -n --all

COMANDO PARA REFRESAR A UN COMMIT ESEPCIFICO SIN GUARDAR TUS CAMBIOS ACTUALES:

    1. git reset --hard <commit>
    (El id del commit se consigue en  source control graph haciendo click derecho sobre el commit )

Para la BD y librerias

pip install pymysql
pip install python-dotenv
pip install flask_sqlalchemy

Advertencias en el cmd
DEBUG: Detalles de bajo nivel, útiles para depurar.
INFO: Información general sobre el funcionamiento de la aplicación.
WARNING: Advertencias sobre algo que podría ser problemático en el futuro.
ERROR: Errores que impiden que una operación se realice correctamente.
CRITICAL: Errores muy graves, típicamente hacen que la aplicación se detenga.



