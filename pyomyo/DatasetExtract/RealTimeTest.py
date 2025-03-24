import time
import numpy as np
import tensorflow as tf
from pyomyo import Myo, emg_mode
from sklearn.preprocessing import MinMaxScaler
from collections import deque
import sys  # Para redirigir la salida

# Diccionario de etiquetas numéricas a nombres de movimiento
prediccion_etiquetas = {
    0: 'Mano Abierta',
    1: 'Mano Cerrada',
    2: 'Punzada Fina',
    3: 'Punzada Gruesa'
}

# Cargar el modelo previamente entrenado
modelo = tf.keras.models.load_model("modelo_completo.keras")

# Normalización con el rango de Myo (0 a 1023)
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(np.array([[0] * 8, [1023] * 8]))  # Ajuste basado en el rango de Myo

# Parámetros para el filtro de ventana deslizante
VENTANA_TIEMPO = 0.5  # Segundos
FRECUENCIA_MUESTRAS = 200  # Myo transmite ~200 muestras por segundo
TAMANO_VENTANA = int(VENTANA_TIEMPO * FRECUENCIA_MUESTRAS)  # 0.5s * 200Hz = 100 muestras

# Buffer para almacenar las últimas muestras
buffer_emg = deque(maxlen=TAMANO_VENTANA)

# Almacenar la última predicción para evitar impresiones innecesarias
ultima_prediccion = None  

def process_data():
    """
    Toma los datos acumulados en el buffer, los promedia y hace la predicción.
    Luego, vacía el buffer para la siguiente captura sin imprimir "clearning".
    """
    global ultima_prediccion, buffer_emg

    if len(buffer_emg) < TAMANO_VENTANA:
        return  # No hacer predicción hasta tener suficientes muestras

    # Convertir buffer a array de numpy
    datos_emg = np.array(buffer_emg, dtype=np.float32)

    # Calcular el promedio en cada canal (se promedia sobre las filas)
    emg_array_promediado = np.mean(datos_emg, axis=0).reshape(1, -1)  # (1, 8)

    # Normalizar datos EMG
    emg_array_norm = scaler.transform(emg_array_promediado)

    # Hacer la predicción con el modelo
    prediccion = modelo.predict(emg_array_norm, verbose=0)  # Obtiene probabilidades
    etiqueta_predicha = np.argmax(prediccion)  # Obtiene la clase con mayor probabilidad

    # Solo imprimir si la predicción ha cambiado
    if etiqueta_predicha != ultima_prediccion:
        print(f"Predicción: {etiqueta_predicha} -> {prediccion_etiquetas[etiqueta_predicha]}")
        ultima_prediccion = etiqueta_predicha  # Actualizar la última predicción

    # Silenciar la salida mientras se vacía el buffer
    sys.stdout = open('/dev/null', 'w') if sys.platform != "win32" else open('nul', 'w')
    buffer_emg.clear()
    sys.stdout = sys.__stdout__  # Restaurar la salida estándar


def main():
    """
    Configura el Myo y comienza la captura de datos en tiempo real.
    """

    global ultima_prediccion, buffer_emg

  
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

    def print_battery(bat):
        print(f"Nivel de batería: {bat}%")

    m.add_battery_handler(print_battery)

    # Configuración del Myo
    m.set_leds([200, 0, 128], [200, 0, 128])  # Color LED
    m.vibrate(1)  # Vibración de confirmación

    print("\nInicio de captura en tiempo real. Presiona Ctrl+C para salir.")

    try:
        while True:
            m.run()  # Ejecuta la lectura en tiempo real
    except KeyboardInterrupt:
        print("\nCaptura finalizada.")

if __name__ == "__main__":
    main()
