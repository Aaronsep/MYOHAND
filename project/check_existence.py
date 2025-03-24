import os

def Existence():
    existe_csv = os.path.isfile("MyoDataset.csv")
    existe_modelo = os.path.isfile("modelo_LSTM.keras")
    return existe_csv, existe_modelo