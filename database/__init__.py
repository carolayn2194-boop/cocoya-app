import shutil
import os
from datetime import datetime


def crear_backup():

    base_datos = "database/cocoya.db"

    # Verificar si la base de datos existe
    if not os.path.exists(base_datos):

        print("⚠️ No existe la base de datos. Backup no realizado.")
        return

    carpeta_backup = "backups"

    # Crear carpeta backups si no existe
    os.makedirs(
        carpeta_backup,
        exist_ok=True
    )

    # Fecha y hora actual
    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    # Nombre del archivo backup
    nombre_backup = f"backup_{fecha}.db"

    # Ruta final del backup
    destino = os.path.join(
        carpeta_backup,
        nombre_backup
    )

    # Copiar base de datos
    shutil.copy2(
        base_datos,
        destino
    )

    print(
        f"✅ Backup creado correctamente: {destino}"
    )


# Ejecutar backup automáticamente
crear_backup()