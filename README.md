# MYOHAND

Sistema de predicción de movimientos de una prótesis robótica de mano utilizando un brazalete Myo y una red neuronal LSTM entrenada con señales EMG.

## Autor

**Nombre:** Aaron Homero Sepúlveda Salcedo  
**Correo:** ahs.mechatronic.eng@gmail.com  
**Fecha:** Marzo 2025  
**Versión:** 1.0

## Descripción General

Este proyecto consiste en un sistema de control para una prótesis de mano que interpreta señales EMG recolectadas desde un brazalete Myo. Las señales son procesadas y utilizadas para entrenar una red neuronal con capas LSTM, permitiendo predecir en tiempo real los movimientos del usuario.

También se desarrolló una interfaz gráfica en Node.js para visualizar y controlar la ejecución del sistema, facilitando la interacción del usuario con el modelo y los dispositivos conectados.

## Estructura del Proyecto

- `project/` - Contiene scripts principales para entrenamiento, prueba y ejecución en tiempo real.
- `pyomyo/` - Módulo para la interfaz con el brazalete Myo.
- `MyoDataset.csv` - Dataset de entrenamiento (si se requiere alojar externamente, mover este archivo).
- `modelo_LSTM.keras` - Modelo entrenado.
- `model_metadata.json` - Información sobre el modelo.
- `requirements.txt` - Dependencias necesarias para ejecutar el proyecto.
- `interface/` - (Si aplica) Contiene los archivos del frontend hecho en Node.js.

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/Aaronsep/MYOHAND.git
   cd MYOHAND
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Para ejecutar la interfaz (si se incluye):
   ```bash
   cd interface
   npm install
   npm start
   ```

## Uso

### 1. Entrenamiento del modelo
Ejecuta el script correspondiente dentro de `project/` para entrenar el modelo con las señales EMG.

### 2. Prueba del modelo
Utiliza los scripts de prueba para validar el rendimiento del modelo con nuevos datos.

### 3. Predicción en tiempo real
Conecta el brazalete Myo y corre el script de predicción en tiempo real (`RealTimeTestv2.py`).

### 4. Interfaz Node.js
Usa la interfaz web desarrollada en Node.js para ejecutar y visualizar los resultados del modelo de forma intuitiva.

## Licencia

Este proyecto no cuenta con una licencia pública aún. Si deseas utilizarlo, contacta al autor.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un *issue* o envía un *pull request*.
