import shutil
import os
from datetime import datetime


def crear_backup():

    base_datos = "database/cocoya.db"

    carpeta_backup = "backups"

    os.makedirs(
        carpeta_backup,
        exist_ok=True
    )

    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    nombre_backup = f"backup_{fecha}.db"

    destino = os.path.join(
        carpeta_backup,
        nombre_backup
    )

    shutil.copy2(
        base_datos,
        destino
    )

    print(
        f"Backup creado: {destino}"
    )


crear_backup()