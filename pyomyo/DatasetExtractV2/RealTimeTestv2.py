import time
import numpy as np
import tensorflow as tf
from pyomyo import Myo, emg_mode
from sklearn.preprocessing import MinMaxScaler
from collections import deque
import sys  # Para actualizar la línea en tiempo real
import os
import requests
import json

url = "https://protesis-c7e62-default-rtdb.firebaseio.com/mensaje.json"

# Diccionario de etiquetas numéricas a nombres de movimiento
prediccion_etiquetas = {
    0: 'Mano Abierta',
    1: 'Mano Cerrada',
    2: 'Punzada Fina',
    3: 'Punzada Gruesa',
    4: 'Mano Adentro',
    5: 'Mano Afuera'
}

# Cargar el modelo LSTM previamente entrenado
modelo = tf.keras.models.load_model("C:/Users/protesis/myoarm/RepoPyoMyo/pyomyo/DatasetExtractV2/modelo_LSTM.keras")

# Normalización con el rango de Myo (0 a 1023)
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(np.array([[0] * 8, [1023] * 8]))  # Ajuste basado en el rango de Myo

# Parámetros de la ventana deslizante
SECUENCIA_LONGITUD = 100  # 100 muestras
VENTANA_TIEMPO = 0.5  # Segundos (100 frames a 200 Hz)
FRECUENCIA_MUESTRAS = 200  # Myo transmite ~200 muestras por segundo
TAMANO_VENTANA = SECUENCIA_LONGITUD  # LSTM ahora usa secuencias de 100 frames
UMBRAL_CONFIANZA = 0.5  # Umbral mínimo de confianza (60%)
DELAY_PREDICCION = 0.1  # 🔹 Menor delay para actualización en tiempo real

# Buffer para almacenar las últimas muestras
buffer_emg = deque(maxlen=TAMANO_VENTANA)

# Almacenar la última predicción para evitar impresiones innecesarias
ultima_prediccion = None
ultima_confianza = 0.0  # Guardar la confianza anterior para actualizar en tiempo real
m = None  # Definir Myo a nivel global para cerrarlo después

import os

def process_data():
    """
    Procesa los datos EMG en tiempo real, actualizando la confianza en la misma línea.
    """
    global ultima_prediccion, ultima_confianza, buffer_emg

    if len(buffer_emg) < TAMANO_VENTANA:
        return  # No hacer predicción hasta tener suficientes muestras

    # Convertir buffer a array de numpy con la forma correcta para LSTM (1, 100, 8)
    datos_emg = np.array(buffer_emg, dtype=np.float32).reshape(1, SECUENCIA_LONGITUD, 8)

    # Normalizar los datos de la secuencia
    datos_emg_norm = scaler.transform(datos_emg.reshape(-1, 8)).reshape(1, SECUENCIA_LONGITUD, 8)

    # Hacer la predicción con el modelo LSTM
    prediccion = modelo.predict(datos_emg_norm, verbose=0)  # Obtiene probabilidades
    prob_max = np.max(prediccion)  # Obtener la mayor probabilidad
    etiqueta_predicha = np.argmax(prediccion)  # Clase con mayor probabilidad

    # Si la confianza es menor al umbral, ignorar la predicción
    if prob_max < UMBRAL_CONFIANZA:
        return

    # 🔹 Actualizar la línea en tiempo real
    sys.stdout.write(f"\rPredicción: {etiqueta_predicha} -> {prediccion_etiquetas[etiqueta_predicha]} (Confianza: {prob_max:.2f})    ")
    sys.stdout.flush()

    sys.stdout.flush()  # Asegurar que la línea se sobrescriba correctamente
    print(etiqueta_predicha)
    data = {"mensaje": int(etiqueta_predicha), 'velocidad': 1}
    requests.put(url, data=json.dumps(data))

    ultima_prediccion = etiqueta_predicha  # Actualizar la última predicción
    ultima_confianza = prob_max  # Actualizar el nivel de confianza

    # 🔹 Delay para evitar que se actualice excesivamente rápido
    time.sleep(DELAY_PREDICCION)

    # 🔹 Capturar salida estándar temporalmente para evitar el mensaje "Clearning"
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # Redirigir salida a /dev/null en Linux/Mac o nul en Windows
    try:
        buffer_emg.clear()
    except:
        pass  # En caso de error, ignorarlo
    sys.stdout = original_stdout  # Restaurar salida estándar


def main():
    """
    Configura el Myo y comienza la captura de datos en tiempo real.
    """
    global ultima_prediccion, buffer_emg, m

    m = Myo(mode=emg_mode.PREPROCESSED)

    # Verificar si hay handlers previos y eliminarlos
    if hasattr(m, 'emg_handlers'):
        m.emg_handlers = []  # Resetear la lista de handlers

    m.connect()

    def add_to_queue(emg, movement):
        """
        Se ejecuta cuando se recibe un dato de EMG.
        Acumula las muestras en un buffer y llama a `process_data()` cuando se llena.
        """
        buffer_emg.append(list(emg))  # Agregar nueva muestra

        if len(buffer_emg) >= TAMANO_VENTANA:
            process_data()  # Procesar los datos cuando se llena la ventana

    m.add_emg_handler(add_to_queue)

    # Configuración del Myo
    m.set_leds([200, 0, 128], [200, 0, 128])  # Color LED
    m.vibrate(1)  # Vibración de confirmación

    print("\nInicio de captura en tiempo real. Presiona Ctrl+C para salir.")

    try:
        while True:
            m.run()  # Ejecuta la lectura en tiempo real
    except KeyboardInterrupt:
        print("\nCaptura finalizada.")
    finally:
        if m is not None:
            print("\nDesconectando Myo...")
            m.disconnect()  # Cerrar el puerto Myo
            print("Myo desconectado correctamente.")

if __name__ == "__main__":
    main()
