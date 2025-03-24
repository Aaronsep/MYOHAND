import multiprocessing
from pyomyo import Myo, emg_mode

def _conexion_worker():
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()
    m.disconnect()

def intentar_conectar(timeout=10):
    p = multiprocessing.Process(target=_conexion_worker)
    p.start()
    p.join(timeout=timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return False
    return True
