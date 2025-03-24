# data_collector.py
import time
import multiprocessing
import numpy as np
import pandas as pd
import msvcrt  # Para detectar teclas en Windows, usa 'input()' si usas otro sistema
import os  # Para manejar archivos

from pyomyo import Myo, emg_mode

# Diccionario de etiquetas numéricas
prediccion_etiquetas = {
    0: 'Mano Abierta',
    1: 'Mano Cerrada',
    2: 'Punzada Fina',
    3: 'Punzada Gruesa',
    4: 'Mano Adentro',
    5: 'Mano Afuera'
}

# Nombre del archivo donde se guardarán todas las muestras
dataset_file = "MyoDataset.csv"

# Definir encabezados globalmente para usarlos en todas las funciones
myo_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4",
            "Channel_5", "Channel_6", "Channel_7", "Channel_8", "Output"]

# ----------- FUNCIÓN PARA CREAR EL CSV SOLO UNA VEZ AL INICIO -------------
def csvcreate():
    if os.path.exists(dataset_file):
        os.remove(dataset_file)  # Eliminar el archivo si existe
        print(f"\nSe eliminó el archivo anterior: '{dataset_file}'")

    # Crear un nuevo archivo vacío con encabezados
    pd.DataFrame(columns=myo_cols).to_csv(dataset_file, index=False)
    print(f"\nSe ha creado un nuevo archivo: '{dataset_file}'")

# ----------- FUNCIÓN PARA TOMAR LECTURAS -------------
def data_worker(mode, seconds, etiqueta_num):

    collect = True
    m = Myo(mode=mode)
    m.connect()

    myo_data = []

    def add_to_queue(emg, movement):
        myo_data.append(list(emg) + [etiqueta_num])

    m.add_emg_handler(add_to_queue)

    m.set_leds([0, 128, 0], [0, 128, 0])
    m.vibrate(1)

    print(f"\nIniciando recolección de datos para: {prediccion_etiquetas[etiqueta_num]}")
    start_time = time.time()

    while collect:
        if (time.time() - start_time < seconds):
            m.run()
        else:
            collect = False
            print(f"\nFinalizó la recolección de datos para: {prediccion_etiquetas[etiqueta_num]}")
            print(f"Tiempo de recolección: {time.time() - start_time:.2f} segundos")
            print(f"{len(myo_data)} frames recogidos")

            # Guardar datos sobrescribiendo el archivo (ya fue recreado)
            myo_df = pd.DataFrame(myo_data, columns=myo_cols)
            myo_df.to_csv(dataset_file, mode='a', header=False, index=False)

            print(f"Datos guardados en {dataset_file}")
