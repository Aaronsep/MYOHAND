# suboff.py
import time
import sys
from pyomyo import Myo, emg_mode

def main():
    try:
        print('Hola')
        m = Myo(mode=emg_mode.RAW)
        m.connect()
        m.vibrate(1)
        time.sleep(2)
        m.power_off()
        sys.exit(0)  # Éxito
    except Exception:
        sys.exit(1)  # Falla

if __name__ == '__main__':
    main()
