import time
import multiprocessing
import numpy as np
import pandas as pd
import msvcrt  # Para detectar teclas en Windows, usa 'input()' si usas otro sistema
import os  # Para verificar si el archivo existe y eliminarlo

from pyomyo import Myo, emg_mode

# Diccionario de etiquetas numéricas
prediccion_etiquetas = {
    0: 'Mano Abierta',
    1: 'Mano Cerrada',
    2: 'Punzada Fina',
    3: 'Punzada Gruesa'
}

# Nombre del archivo donde se guardarán todas las muestras
dataset_file = "MyoDataset.csv"

# ----------- VERIFICAR SI EL ARCHIVO EXISTE Y DECIDIR QUÉ HACER -------------
if os.path.exists(dataset_file):
    print(f"\nEl archivo '{dataset_file}' ya existe.")
    print("¿Qué deseas hacer?")
    print("[A] Continuar escribiendo en el archivo existente")
    print("[B] Borrar y crear un nuevo archivo vacío")

    while True:
        opcion = input("\nSelecciona una opción (A/B): ").strip().upper()
        if opcion in ["A", "B"]:
            break
        print("Opción inválida. Ingresa 'A' o 'B'.")

    if opcion == "B":
        os.remove(dataset_file)
        print(f"\nEl archivo '{dataset_file}' ha sido eliminado. Creando uno nuevo...")

# Si el archivo no existe o fue eliminado, crear uno nuevo con encabezados
if not os.path.exists(dataset_file):
    myo_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4",
                "Channel_5", "Channel_6", "Channel_7", "Channel_8", "Output"]
    pd.DataFrame(columns=myo_cols).to_csv(dataset_file, index=False)
    print(f"\nSe ha creado el archivo '{dataset_file}'.")

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

            # Guardar datos en CSV sin sobrescribir
            myo_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4",
                        "Channel_5", "Channel_6", "Channel_7", "Channel_8", "Output"]
            myo_df = pd.DataFrame(myo_data, columns=myo_cols)

            existing_df = pd.read_csv(dataset_file)
            myo_df = pd.concat([existing_df, myo_df], ignore_index=True)
            myo_df.to_csv(dataset_file, index=False)

            print(f"Datos guardados en {dataset_file}")

# ----------- INICIAR TOMA DE LECTURAS -------------
if __name__ == '__main__':
    seconds = 10
    mode = emg_mode.PREPROCESSED

    for etiqueta_num in range(4):  # 0, 1, 2, 3
        print(f"\nPresiona cualquier tecla para comenzar la recolección de datos para: {prediccion_etiquetas[etiqueta_num]}")
        
        # Esperar a que el usuario presione una tecla antes de cada registro
        msvcrt.getch()  # En Windows, usa 'input()' si estás en Linux o macOS
        
        p = multiprocessing.Process(target=data_worker, args=(mode, seconds, etiqueta_num))
        p.start()
        p.join()  # Espera a que termine antes de continuar con la siguiente ejecución

        print(f"\nRecolección de {prediccion_etiquetas[etiqueta_num]} completada. Pasando al siguiente movimiento.")
    
    print("\nProceso de recolección completado. Todos los datos están en 'MyoDataset.csv'.")
