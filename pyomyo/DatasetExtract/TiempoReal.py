import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import serial
import numpy as np
from tensorflow.keras.models import load_model
from scipy.fft import fft
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Cargar el modelo previamente entrenado
model = load_model('modelo_completo.h5')

# Diccionario para traducir la predicción a su correspondiente nombre
prediccion_etiquetas = {
    0: 'Mano Abierta',
    1: 'Mano Cerrada',
    2: 'Punzada Fina',
    3: 'Punzada Gruesa'
}

# Configuración del puerto serie
ser = serial.Serial('COM4', 9600)  # Cambia 'COM4' por tu puerto

# Crear la ventana principal
root = tk.Tk()
root.title("Interfaz de Predicción de Mano")
root.geometry("800x700")

# Etiqueta de imagen
etiqueta_imagen = tk.Label(root)
etiqueta_imagen.pack(pady=20)

# Etiqueta de predicción
etiqueta_prediccion = tk.Label(root, text="Predicción: ", font=("Helvetica", 16))
etiqueta_prediccion.pack(pady=20)

# Etiqueta de valores de entrada
etiqueta_numeric_data = tk.Label(root, text="Valores de los Sensores: ", font=("Helvetica", 12))
etiqueta_numeric_data.pack(pady=10)

# Figura para el heatmap
fig = plt.Figure(figsize=(6, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# Tiempo entre predicciones (en segundos)
tiempo_entre_predicciones = 0.1
ultimo_muestreo = time.time()

# Funciones para calcular características
def compute_emg_features(signal):
    return [
        np.mean(np.abs(signal)),  # MAV
        np.var(signal),          # VAR
        np.std(signal),          # SD
        np.sqrt(np.mean(signal ** 2)),  # RMS
        np.sum(np.abs(np.diff(signal))),  # WL
        np.sum(np.diff(np.sign(signal)) != 0)  # ZC
    ]

def fft_features(signal):
    fft_result = fft(signal)
    fft_abs = np.abs(fft_result)
    fft_freq = np.fft.fftfreq(len(signal))
    return [
        np.max(fft_abs),                  # Max Amplitude
        fft_freq[np.argmax(fft_abs)]      # Peak Frequency
    ]

def actualizar_interfaz(data, numeric_data, prediccion_nombre, prediction):
    # Actualizar la predicción en la interfaz
    etiqueta_prediccion.config(text=f"Predicción: {prediccion_nombre}")
    
    # Actualizar los valores de los sensores
    numeric_data_text = ', '.join([f"Sensor{i+1}: {value:.2f}" for i, value in enumerate(numeric_data)])
    etiqueta_numeric_data.config(text=f"Valores de los Sensores: {numeric_data_text}")
    
    # Actualizar el heatmap
    ax = fig.add_subplot(111)
    ax.clear()
    ax.set_title("Distribución de Probabilidades")
    ax.set_xlabel("Clases")
    ax.set_ylabel("Probabilidad")
    etiquetas = list(prediccion_etiquetas.values())
    ax.bar(etiquetas, prediction[0], color="skyblue")
    ax.set_ylim(0, 1)  # Las probabilidades están entre 0 y 1
    canvas.draw()

while True:
    try:
        # Leer línea del puerto serie
        line = ser.readline().decode('utf-8').strip()

        # Dividir la línea por comas y convertir a flotantes
        data = list(map(float, line.split(',')))

        # Verificar si se obtienen al menos 4 sensores
        if len(data) >= 4 and time.time() - ultimo_muestreo >= tiempo_entre_predicciones:
            # Calcular características
            features = compute_emg_features(data) + fft_features(data)
            features = np.array(features).reshape(1, -1)

            # Predicción del modelo
            prediction = model.predict(features)
            pred_class = np.argmax(prediction, axis=1)[0]
            prediccion_nombre = prediccion_etiquetas.get(pred_class, "Desconocido")

            # Actualizar la interfaz gráfica
            actualizar_interfaz(data, data, prediccion_nombre, prediction)
            ultimo_muestreo = time.time()

        # Actualizar la interfaz de Tkinter
        root.update()

    except KeyboardInterrupt:
        print("Finalizando...")
        break

ser.close()
