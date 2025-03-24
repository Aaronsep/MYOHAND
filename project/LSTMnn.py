import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, GlobalAveragePooling1D
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


def train():

    # Cargar datos
    filepath = 'MyoDataset.csv'
    df = pd.read_csv(filepath)

    df = df.iloc[:, :9]  # Solo tomar los 8 sensores y la etiqueta

    # Separar datos de entrada (X) y salida (y)
    X = df.iloc[:, :-1].values  # Entradas (8 sensores EMG)
    y = df.iloc[:, -1].values  # Etiquetas
    y = to_categorical(y, num_classes=6)  # Convertir etiquetas a one-hot

    # Normalizar los datos de entrada entre 0 y 1
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(np.array([[0] * 8, [1023] * 8]))  # Ajuste basado en Myo
    X_normalized = scaler.transform(X)

    # Reformatear los datos para LSTM (ventanas de tiempo)
    SECUENCIA_LONGITUD = 100  # Número de frames por ventana
    X_seq = []
    y_seq = []

    # Crear ventanas de secuencias
    for i in range(len(X_normalized) - SECUENCIA_LONGITUD):
        X_seq.append(X_normalized[i:i+SECUENCIA_LONGITUD])  # Secuencia de 10 frames
        y_seq.append(y[i+SECUENCIA_LONGITUD])  # Etiqueta asociada al último frame

    X_seq = np.array(X_seq)  # Convertir a numpy array
    y_seq = np.array(y_seq)


    # Dividir en entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)

    y_labels = np.argmax(y_train, axis=1)
    
    def add_gaussian_noise(data, mean=0, std=0.05):
        """
        Agrega ruido gaussiano a los datos EMG.
        """
        noise = np.random.normal(mean, std, data.shape)
        return data + noise

    def apply_jitter(data, jitter_strength=0.05):
        """
        Aplica un desplazamiento aleatorio a la señal.
        """
        jitter = np.random.uniform(-jitter_strength, jitter_strength, size=data.shape)
        return data + jitter

    def scale_signal(data, scale_min=0.8, scale_max=1.2):
        """
        Aplica un factor de escala aleatorio a los datos.
        """
        scale_factor = np.random.uniform(scale_min, scale_max)
        return data * scale_factor

    def time_warping(data, sigma=0.2):
        """
        Simula pequeñas deformaciones temporales en la señal EMG.
        sigma: Controla la cantidad de deformación aplicada.
        """
        # Crear una transformación aleatoria de los índices temporales
        indices = np.arange(len(data))
        new_indices = indices + np.random.normal(0, sigma, size=len(indices))
        new_indices = np.clip(new_indices, 0, len(data) - 1)  # Evitar valores fuera del rango

        # Si `data` es 2D (Ej: `(100, 8)`), aplicamos `np.interp()` a cada columna
        if data.ndim == 2:
            warped_data = np.zeros_like(data)
            for i in range(data.shape[1]):  # Iteramos por cada canal EMG
                warped_data[:, i] = np.interp(indices, new_indices, np.interp(new_indices, indices, data[:, i]))
            return warped_data
        else:
            return np.interp(indices, new_indices, np.interp(new_indices, indices, data))
        
    def permute_segments(data, n_segments=4):
        """
        Divide la señal en segmentos y los reordena aleatoriamente.
        """
        segment_length = data.shape[0] // n_segments
        segments = [data[i*segment_length:(i+1)*segment_length] for i in range(n_segments)]
        np.random.shuffle(segments)
        return np.concatenate(segments, axis=0)

    def partial_flip(data, flip_ratio=0.3):
        """
        Invierte aleatoriamente una porción de la señal en el tiempo.
        """
        length = data.shape[0]
        flip_size = int(length * flip_ratio)
        start = np.random.randint(0, length - flip_size)
        flipped = data.copy()
        flipped[start:start+flip_size] = flipped[start:start+flip_size][::-1]
        return flipped

    def temporal_dropout(data, drop_prob=0.1):
        """
        Elimina aleatoriamente algunos puntos temporales (los reemplaza por 0).
        """
        mask = np.random.rand(*data.shape) > drop_prob
        return data * mask

    def augment_specific_classes(X, y_labels, target_classes=[2, 3], times_per_sample=1, num_classes=6):

        """
        Aplica data augmentation solo a las clases especificadas.
        
        Parámetros:
        - X: np.array de forma (N, 100, 8)
        - y_labels: array plano de clases (shape: N,)
        - target_classes: lista con clases objetivo (por defecto: [2, 3])
        - times_per_sample: cuántas veces aumentar cada muestra objetivo
        - num_classes: total de clases para codificación one-hot
        
        Retorna:
        - X_final, y_final: datos originales + aumentados
        """
        X_aug = []
        y_aug = []

        for x, y in zip(X, y_labels):
            if y in target_classes:
                for _ in range(times_per_sample):
                    x_aug = augment_data(x)
                    X_aug.append(x_aug)
                    y_aug.append(y)

        X_aug = np.array(X_aug)
        y_aug = np.array(y_aug)
        y_aug_onehot = tf.keras.utils.to_categorical(y_aug, num_classes=num_classes)

        # Codifica los originales si es necesario
        y_orig_onehot = tf.keras.utils.to_categorical(y_labels, num_classes=num_classes)

        X_final = np.concatenate([X, X_aug], axis=0)
        y_final = np.concatenate([y_orig_onehot, y_aug_onehot], axis=0)

        return X_final, y_final, X_aug, y_aug_onehot


    def augment_data(data):
        if np.random.rand() < 0.8:
            data = add_gaussian_noise(data, std=0.05)
        if np.random.rand() < 0.6:
            data = apply_jitter(data, jitter_strength=0.05)
        if np.random.rand() < 0.6:
            data = scale_signal(data)
        if np.random.rand() < 0.5:
            data = time_warping(data)
        if np.random.rand() < 0.4:
            data = permute_segments(data)
        if np.random.rand() < 0.3:
            data = partial_flip(data)
        if np.random.rand() < 0.2:
            data = temporal_dropout(data)
        return data

    X_train_l = np.array([augment_data(x) for x in X_train])
    X_train_final, y_train_final, X_train_augmented, y_train_augmented = augment_specific_classes(X_train_l, y_labels, target_classes=[0,2, 3])

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(100, 8), kernel_regularizer=l2(0.01)),
        BatchNormalization(),
        Dropout(0.3),

        LSTM(32, return_sequences=True, kernel_regularizer=l2(0.01)),
        BatchNormalization(),
        Dropout(0.3),

        GlobalAveragePooling1D(),

        Dense(32, activation='relu', kernel_regularizer=l2(0.01)),
        BatchNormalization(),
        Dropout(0.2),

        Dense(6, activation='softmax')
])

    # Compilar el modelo
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # Agregar Early Stopping para detener entrenamiento si el modelo empieza a sobreajustar

    early_stopping = EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3)
    checkpoint = ModelCheckpoint(
        filepath='modelo_LSTM.keras',
        monitor='val_accuracy',
        save_best_only=True,
        save_weights_only=False
    )

    callbacks = [early_stopping, reduce_lr, checkpoint]

    # Entrenar el modelo
    history = model.fit(X_train_final, y_train_final, 
                        epochs=30, 
                        batch_size=32, 
                        validation_data=(X_test, y_test), 
                        callbacks=callbacks)

    # Evaluar el modelo en el conjunto de prueba
    loss, accuracy = model.evaluate(X_test, y_test)

    # Evaluar en el conjunto de testeo
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=2)

    ta = round(test_accuracy*100)

    return True, ta