# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import multiprocessing
from pyomyo import emg_mode
from data_collector import data_worker, csvcreate
from LSTMnn import train
from poweroff import power_off_myo
from check_existence import Existence
import json
import os
from reconectar import intentar_conectar 
import threading

selfbuffer = {}

if os.path.exists('model_metadata.json'):
    with open('model_metadata.json', 'r') as f:
        selfbuffer = json.load(f)



app = Flask(__name__)
CORS(app)

@app.route('/api/reconnect', methods=['POST'])
def reconnect():
    try:
        if intentar_conectar():
            return jsonify({"status": "reconnected"}), 200
        else:
            return jsonify({"error": "No se pudo reconectar al Myo"}), 408  # Timeout
    except Exception as e:
        return jsonify({"error": "Falló la reconexión", "details": str(e)}), 500


@app.route('/api/get-accuracy', methods=['POST'])
def get_accuracy():
    try:
        with open('model_metadata.json', 'r') as f:
            data = json.load(f)
        accuracy = data.get('accuracy', None)
        if accuracy is not None:
            return jsonify({"accuracy": accuracy}), 200
        else:
            return jsonify({"error": "Accuracy no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

realtime_process = None

@app.route('/api/realtime', methods=['POST'])
def realtime():
    global realtime_process
    from RealTimeTestv2 import tiemporeal

    if realtime_process is None or not realtime_process.is_alive():
        realtime_process = multiprocessing.Process(target=tiemporeal)
        realtime_process.start()
        return jsonify({"message": "Ejecución en tiempo real iniciada"}), 200
    else:
        realtime_process.terminate()
        realtime_process.join()
        return jsonify({"message": "Ejecución en tiempo real detenida"}), 200


@app.route('/api/train-model', methods=['POST'])
def train_model():
    try:
        success, val_acc = train()
        if success is True:
            ta = val_acc            
            # Guardar en archivo
            with open('model_metadata.json', 'w') as f:
                json.dump({"accuracy": ta}, f)

            return jsonify({"status": "training_completed"}), 200
        else:
            return jsonify({"error": "Training failed"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/check', methods=['GET'])
def checkexistence():
    print('bandera')
    try:
        csv_existe, modelo_existe = Existence()
        return {
            'MyoDataset.csv': csv_existe,
            'modelo_LSTM.keras': modelo_existe
        }, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/power-off', methods=['POST'])
def power_off():
    if power_off_myo():
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'success'}), 200


@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    data = request.get_json()
    etiqueta_num = data.get('step')

    if etiqueta_num is None or etiqueta_num not in range(6):
        return jsonify({"error": "Paso inválido"}), 400

    # Solo en la primera recolección
    if etiqueta_num == 0:
        csvcreate()

    mode = emg_mode.PREPROCESSED
    seconds = 10
    max_retries = 3

    for attempt in range(max_retries):
        p = multiprocessing.Process(target=data_worker, args=(mode, seconds, etiqueta_num))
        p.start()
        p.join(seconds + 15)
        if p.is_alive():
            p.terminate()
            print(f"Intento {attempt+1} fallido, se superó el tiempo límite. Reintentando...")
        else:
            return jsonify({"status": "completed", "step": etiqueta_num}), 200

    return jsonify({"error": "Recolección de datos tardó demasiado, se canceló tras varios intentos."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
