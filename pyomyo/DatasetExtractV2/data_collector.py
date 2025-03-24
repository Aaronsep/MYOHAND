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
dataset_file = "C:/Users/protesis/myoarm/RepoPyoMyo/pyomyo/DatasetExtractV2/MyoDataset.csv"

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

    # ------------ Configuración de Myo ---------------
    m = Myo(mode=mode)
    m.connect()

    myo_data = []

    def add_to_queue(emg, movement):
        myo_data.append(list(emg) + [etiqueta_num])  # Convertir 'emg' a lista y agregar la etiqueta numérica

    m.add_emg_handler(add_to_queue)

    def print_battery(bat):
        print("Battery level:", bat)

    m.add_battery_handler(print_battery)

    # Configuración de LED y vibración para indicar conexión
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

            # Guardar datos en el CSV sin sobrescribir encabezados
            myo_df = pd.DataFrame(myo_data, columns=myo_cols)
            myo_df.to_csv(dataset_file, mode='a', header=False, index=False)  # Agregar datos sin sobrescribir el archivo

            print(f"Datos guardados en {dataset_file}")

# ----------- INICIAR TOMA DE LECTURAS -------------
if __name__ == '__main__':
    # Crear CSV solo una vez al inicio
    csvcreate()

    # Tiempo de captura y configuración del Myo
    seconds = 10
    mode = emg_mode.PREPROCESSED

    for etiqueta_num in range(len(prediccion_etiquetas)):  # 0, 1, 2, 3
        print(f"\nPresiona cualquier tecla para comenzar la recolección de datos para: {prediccion_etiquetas[etiqueta_num]}")
        
        # Esperar a que el usuario presione una tecla antes de cada registro
        msvcrt.getch()  # En Windows, usa 'input()' si estás en Linux o macOS
        
        p = multiprocessing.Process(target=data_worker, args=(mode, seconds, etiqueta_num))
        p.start()
        p.join()  # Espera a que termine antes de continuar con la siguiente ejecución

        print(f"\nRecolección de {prediccion_etiquetas[etiqueta_num]} completada. Pasando al siguiente movimiento.")
    
    print("\nProceso de recolección completado. Todos los datos están en 'MyoDataset.csv'.")
