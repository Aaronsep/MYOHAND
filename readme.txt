# 📌 DOCUMENTACIÓN DEL SISTEMA EMG - PREDICCIÓN DE MOVIMIENTOS DE MANO
**Autor:** Aaron Homero Sepúlveda Salcedo  
**Fecha:** 20-03-2025
**Versión:** 2.0  
**Descripción:** Este documento describe el flujo de trabajo del sistema basado en señales EMG, que incluye la recolección de datos, el entrenamiento de una red LSTM y la predicción en tiempo real.

---

## 📌 FLUJO GENERAL DEL SISTEMA
El sistema de predicción de movimientos de la mano basado en señales EMG consta de **tres fases principales**:

1️⃣ **Recolección de datos** (`data_collector.py`)  
2️⃣ **Entrenamiento del modelo LSTM** (`LSTMnn.py`)  
3️⃣ **Predicción en tiempo real** (`RealTimeTestv2.py`)  

Cada uno de estos pasos es fundamental para garantizar la precisión del modelo.

---

## 1️⃣ RECOLECCIÓN DE DATOS - `data_collector.py`
**Objetivo:** Capturar señales EMG desde el sensor Myo y almacenarlas en un archivo CSV con etiquetas correspondientes a cada movimiento.

### 🔹 Funcionamiento
1. Se conecta el sensor **Myo Armband** al sistema.
2. El usuario realiza **movimientos específicos de la mano**, y el programa captura **los datos de los 8 sensores EMG**.
3. Cada muestra incluye:
   - **8 valores de EMG** (uno por canal)
   - **Etiqueta de la clase** (ej: "Mano Abierta", "Punzada Fina")
4. Se almacenan los datos en `MyoDataset.csv`, el cual se **sobrescribe** cada vez que se ejecuta el programa para garantizar que los datos sean nuevos y actualizados.

### 🔹 Código clave
- **Captura de datos EMG**
  ```python
  m.add_emg_handler(add_to_queue)
  ```
- **Guardado en CSV**
  ```python
  pd.DataFrame(myo_data, columns=myo_cols).to_csv(dataset_file, mode='a', header=False, index=False)
  ```

---

## 2️⃣ ENTRENAMIENTO DEL MODELO LSTM - `LSTMnn.py`
**Objetivo:** Entrenar una red neuronal **LSTM** para aprender patrones en las señales EMG y predecir los movimientos de la mano.

### 🔹 Funcionamiento
1. Se carga el dataset `MyoDataset.csv` y se **preprocesan los datos**.
2. Se normalizan los valores EMG para que estén en un rango **0 a 1**.
3. Se estructura el dataset en **secuencias de 100 muestras** para alimentar la LSTM.
4. Se entrena una **red neuronal LSTM** con `TensorFlow` para predecir la etiqueta de cada movimiento.
5. Se guarda el modelo entrenado en `modelo_LSTM.keras` para su uso en predicciones en tiempo real.

### 🔹 Evaluación del Modelo
Se evalúa el rendimiento con **precisión (`accuracy`) y pérdida (`loss`)** en el dataset de validación.

```python
modelo.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_val, y_val), callbacks=[early_stopping])
```

---

## 3️⃣ PREDICCIÓN EN TIEMPO REAL - `RealTimeTestv2.py`
**Objetivo:** Utilizar el modelo `modelo_LSTM.keras` para predecir en tiempo real los movimientos de la mano basados en señales EMG.

### 🔹 Funcionamiento
1. Se conecta el **Myo Armband** al sistema.
2. Se almacena una **ventana de 100 muestras** en un buffer (`deque`).
3. Cada 0.5 segundos, se normaliza y procesa la señal para enviarla al modelo LSTM.
4. Se obtiene la predicción **con confianza** (`softmax`) y se actualiza en pantalla.
5. Se limpia el buffer y se vuelve a capturar.

### 🔹 Implementación de la Predicción
- **Captura de datos en tiempo real**
  ```python
  buffer_emg.append(list(emg))
  if len(buffer_emg) >= TAMANO_VENTANA:
      process_data()
  ```
- **Predicción con la LSTM**
  ```python
  prediccion = modelo.predict(datos_emg_norm, verbose=0)
  etiqueta_predicha = np.argmax(prediccion)
  ```
- **Manejo de confianza mínima**
  ```python
  if prob_max < UMBRAL_CONFIANZA:
      return  # Ignorar predicción poco confiable
  ```
- **Visualización de predicciones en tiempo real**
  ```python
  sys.stdout.write(f"\rPredicción: {etiqueta_predicha} -> {prediccion_etiquetas[etiqueta_predicha]} (Confianza: {prob_max:.2f})")
  sys.stdout.flush()
  ```

---

## 🔹 MEJORAS FUTURAS
Para mejorar la precisión y estabilidad del sistema, se pueden aplicar las siguientes técnicas:
✅ **Data Augmentation**: Agregar ruido, distorsión temporal y escalado de señales para mejorar la robustez del modelo.  
✅ **Optimización del Modelo**: Ajustar hiperparámetros como el tamaño de la LSTM, tasa de aprendizaje y función de activación.  
✅ **Filtro pasa-bajas**: Para eliminar ruido en la señal EMG antes de la normalización.  
✅ **Matriz de Confusión**: Evaluar qué clases se están confundiendo más para mejorar el dataset.  

---

## 📌 CONCLUSIÓN
Este sistema **utiliza señales EMG capturadas en tiempo real para predecir movimientos de la mano con una red LSTM**. A través de la recolección de datos, entrenamiento y predicción en tiempo real, se obtiene un modelo que puede identificar **cuatro movimientos diferentes** con alta precisión. 

Con más mejoras en los datos y la arquitectura del modelo, este sistema tiene potencial para aplicaciones en **prótesis controladas por EMG, interfaces cerebro-máquina y rehabilitación neuromuscular**.

🚀 **Fin del documento** 🚀
