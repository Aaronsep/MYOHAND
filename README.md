# MYOHAND

## Descripción en Español

Sistema impulsado por inteligencia artificial para controlar una mano protésica robótica mediante señales EMG de un brazalete Myo. Utiliza redes neuronales LSTM para la predicción de gestos en tiempo real e incluye una interfaz gráfica en Node.js para mejorar la interacción del usuario. Desarrollado con la librería MyoPyO.

### Autores

**Nombres:** Aaron Homero Sepúlveda Salcedo, Jesus Alejandro Ocegueda Melin, Fernando Vidal Luna Jaime & Oxcel Alejandro Galvan Rendon
**Correos:** ahs.mechatronic.eng@gmail.com & Oceguedaalejandro12@gmail.com <br>
**Fecha:** Marzo 2025  
**Versión:** 1.0

### Descripción General del Proyecto

Este proyecto es un sistema de control para una mano protésica robótica que interpreta señales EMG captadas por un brazalete Myo. Estas señales se procesan y se introducen en una red neuronal basada en LSTM para predecir gestos de la mano en tiempo real.

Una interfaz gráfica desarrollada en Node.js permite a los usuarios operar y monitorear el sistema de manera sencilla.

### Estructura del Proyecto

- `project/` - Scripts en Python para entrenamiento, prueba y predicción en tiempo real.
- `pyomyo/` - Librería de interfaz con el brazalete Myo.
- `MyoDataset.csv` - Conjunto de datos EMG para entrenamiento.
- `modelo_LSTM.keras` - Archivo del modelo entrenado.
- `model_metadata.json` - Metadatos del modelo.
- `requirements.txt` - Dependencias de Python.
- `interface/` - Interfaz gráfica en Node.js.

### Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Aaronsep/MYOHAND.git
   cd MYOHAND
   ```

2. (Opcional) Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Para iniciar la interfaz:
   ```bash
   cd interface
   npm install
   npm start
   ```

### Uso

1. **Entrenamiento del Modelo**  
   Ejecuta el script correspondiente dentro de la carpeta `project/`.

2. **Prueba del Modelo**  
   Usa los scripts de prueba para validar el rendimiento del modelo con nuevos datos.

3. **Predicción en Tiempo Real**  
   Conecta el brazalete Myo y ejecuta `RealTimeTestv2.py`.

4. **Interfaz Node.js**  
   Usa la interfaz para operar el sistema fácilmente.


### 🔧 Ejecución en Raspberry Pi

El archivo `firebaseconnect3.py`, ubicado en la Raspberry Pi, es el encargado de:

- Leer los datos de movimiento desde Firebase.  
- Controlar la lógica de movimiento del carrito en tiempo real.

Para iniciar el sistema en la Raspberry Pi, ejecuta:

```bash
python3 /home/USUARIO/firebaseconnect3.py
```

Este archivo debe estar corriendo en todo momento para que el sistema funcione correctamente.


### Licencia

Este proyecto aún no tiene una licencia pública. Contacta al autor para solicitar permisos.

### Contribuciones

Las contribuciones son bienvenidas. Abre un issue o envía un pull request.

---

## English Description

AI-powered system for controlling a robotic prosthetic hand using EMG signals from a Myo armband. It leverages LSTM neural networks for real-time gesture prediction and includes a Node.js graphical interface for enhanced user interaction. Built with the MyoPyO library.

### Authors

**Names:** Aaron Homero Sepúlveda Salcedo, Jesus Alejandro Ocegueda Melin, Fernando Vidal Luna Jaime & Oxcel Alejandro Galvan Rendon
**Emails:** ahs.mechatronic.eng@gmail.com & Oceguedaalejandro12@gmail.com <br>
**Date:** March 2025  
**Version:** 1.0

### Project Overview

This project is a control system for a robotic prosthetic hand that interprets EMG signals captured by a Myo armband. These signals are processed and fed into an LSTM-based neural network to predict hand gestures in real time.

A graphical user interface developed in Node.js allows users to easily operate and monitor the system.

### Project Structure

- `project/` - Python scripts for training, testing, and real-time prediction.
- `pyomyo/` - Myo armband interface library.
- `MyoDataset.csv` - EMG dataset for training.
- `modelo_LSTM.keras` - Trained model file.
- `model_metadata.json` - Model metadata.
- `requirements.txt` - Python dependencies.
- `interface/` - Node.js graphical interface.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Aaronsep/MYOHAND.git
   cd MYOHAND
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. To launch the interface:
   ```bash
   cd interface
   npm install
   npm start
   ```

### Usage

1. **Model Training**  
   Run the training script inside the `project/` folder.

2. **Model Testing**  
   Use the testing scripts to validate model performance on new data.

3. **Real-Time Prediction**  
   Connect the Myo armband and run `RealTimeTestv2.py`.

4. **Node.js Interface**  
   Use the interface to operate the system easily.


### 🔧 Raspberry Pi Execution

The file `firebaseconnect3.py`, located on the Raspberry Pi, is responsible for:

- Reading movement data from Firebase.  
- Managing the cart's real-time motion logic.

To start the system on the Raspberry Pi, run:

```bash
python3 /home/USER/firebaseconnect3.py
```

This file must be running at all times for the system to function properly.


### License

This project is not yet licensed. Contact the author for permissions.

### Contributions

Contributions are welcome. Open an issue or submit a pull request.
