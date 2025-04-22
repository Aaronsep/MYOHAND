import requests
import sseclient
import json
import numpy as np

try:
    import smbus2 as smbus
    bus = smbus.SMBus(1)
except:
    class FakeBus:
        def write_i2c_block_data(self, addr, reg, data):
            print(f"[Simulacion] I2C -> Addr: {hex(addr)}, Reg: {hex(reg)}, Data: {data}")
    bus = FakeBus()

FIREBASE_STREAM_URL = "https://robomesha-default-rtdb.firebaseio.com/comandos/robomesha.json"
DIRECCION_MOTORES = 0x34
REG_VELOCIDAD_FIJA = 0x33

R = 0.048
l1 = 0.097
l2 = 0.109

W = (1 / R) * np.array([
    [1, 1, -(l1 + l2)],
    [1, 1, (l1 + l2)],
    [1, -1, (l1 + l2)],
    [1, -1, -(l1 + l2)]
])

V_MAX = 250
PWM_MAX = 100

estado_actual = {
    "vx": 0,
    "vy": 0,
    "w": 0,
    "accion": "detener"
}

vx_ant, vy_ant, omega_ant = None, None, None

def calcular_pwm(vx, vy, omega):
    V = np.array([vx, vy, omega])
    velocidades = np.dot(W, V)
    factor_escala = np.max(np.abs(velocidades)) / 250 if np.max(np.abs(velocidades)) > 250 else 1
    if factor_escala > 1:
        velocidades /= factor_escala
    velocidades[1] *= -1
    velocidades[2] *= -1
    pwm = np.clip((velocidades / V_MAX) * PWM_MAX, -PWM_MAX, PWM_MAX)
    return [int(p) for p in pwm]

def enviar_pwm(vx, vy, omega):
    pwm_values = calcular_pwm(vx, vy, omega)
    try:
        bus.write_i2c_block_data(DIRECCION_MOTORES, REG_VELOCIDAD_FIJA, pwm_values)
    except:
        print("Error I2C al enviar PWM.")

def detener_motores():
    try:
        bus.write_i2c_block_data(DIRECCION_MOTORES, REG_VELOCIDAD_FIJA, [0, 0, 0, 0])
    except:
        print("Error I2C al detener motores.")

def escuchar_firebase():
    global vx_ant, vy_ant, omega_ant

    session = requests.Session()
    response = session.get(FIREBASE_STREAM_URL, stream=True, headers={"Accept": "text/event-stream"})
    client = sseclient.SSEClient(response)

    print("Escuchando cambios en Firebase...")
    for event in client.events():
        if event.event == "put":
            try:
                payload = json.loads(event.data)
                path = payload.get("path", "")
                data = payload.get("data", {})

                if path == "/" and isinstance(data, dict):
                    estado_actual.update(data)
                elif isinstance(data, (int, float, str)) and path.startswith("/"):
                    clave = path.strip("/")
                    estado_actual[clave] = data

                if estado_actual.get("accion") == "mover":
                    vx = int(estado_actual.get("vx", 0))
                    vy = int(estado_actual.get("vy", 0))
                    omega = int(estado_actual.get("w", 0))

                    if (vx, vy, omega) != (vx_ant, vy_ant, omega_ant):
                        enviar_pwm(vx, vy, omega)
                        print(f"PWM actualizado: vx={vx}, vy={vy}, omega={omega}")
                        vx_ant, vy_ant, omega_ant = vx, vy, omega

                elif estado_actual.get("accion") == "detener":
                    if (vx_ant, vy_ant, omega_ant) != (0, 0, 0):
                        detener_motores()
                        print("Motores detenidos por comando.")
                        vx_ant, vy_ant, omega_ant = 0, 0, 0

            except Exception as e:
                print(f"Error al procesar evento: {e}")

if __name__ == "__main__":
    try:
        escuchar_firebase()
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
    finally:
        detener_motores()
        print("Motores apagados.")
