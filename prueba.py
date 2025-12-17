import serial   ##pynput y pyserial
import time
import serial.tools.list_ports

from pynput.mouse import Controller
from pynput.keyboard import Listener, Key

import re
import threading

salir = False
mouse = Controller()

##suavizado
alpha = 0.01
sx, sy = 0, 0
deadzone = 500


def on_press(key):
    global salir
    if key == Key.esc:
        print("Tecla ESC presionada. Saliendo...")
        salir = True
        return False  # Detiene el listener


def get_variables(data_bytes):
    data_str = data_bytes.decode("utf-8").strip()
    numeros = re.findall(r"-?\d+\.?\d*", data_str)
    if len(numeros) != 6:
        raise ValueError(f"No se encontraron exactamente dos números en: {data_str}")
    return float(numeros[0]), float(numeros[1]), float(numeros[2]), float(numeros[3]), float(numeros[4]), float(numeros[5])



def find_arduino():
    """Busca el puerto donde está conectado Arduino."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Arduino suele tener 'Arduino' en la descripción o un VID/PID conocido
        if 'Arduino' in port.description or 'ttyACM' in port.device or 'ttyUSB' in port.device:
            return port.device
    return None



def suavizar_movimiento(x, y, last_x, last_y):
    # aplicar deadzone
    if abs(x - last_x) < deadzone:
        x = last_x
    if abs(y - last_y) < deadzone:
        y = last_y

    # filtro low-pass
    global sx, sy
    sx = alpha * x + (1 - alpha) * sx
    sy = alpha * y + (1 - alpha) * sy
    
    return sx, sy




# Buscar el Arduino
arduino_port = find_arduino()


if arduino_port is None:
    print("No se encontró ningún Arduino conectado.")
else:
    print(f"Arduino encontrado en: {arduino_port}")
    # Conectar al Arduino
    try:
        keyboard_listener = Listener(on_press=on_press)
        keyboard_listener.start()


        arduino = serial.Serial(arduino_port, 115200, timeout=1)
        arduino.flush()

        print("Leyendo datos del Arduino (CTRL+C para salir)...")


        cad1 = arduino.readline().strip()
        cad1 = arduino.readline().strip()
        cad1 = arduino.readline().strip()
        cad1 = arduino.readline().strip()
        cad1 = arduino.readline().strip()
        print(cad1)



        while not salir:
            cad = arduino.readline()
            if not cad:  # ignorar líneas vacías
                continue
            try:




                #x, y , z, a,b , c= get_variables(cad)
                #x*=180
                #y*=180
                #ox, oy = mouse.position
                #print(cad)
                x, y , z, a,b , c= get_variables(cad)
                print("aña",x,y,z, a, b, c)
                #x, y = suavizar_movimiento(x,y,ox,oy)
                #mouse.position = (x, y)
            except ValueError:
            # Si la línea no tiene 2 números, simplemente la ignoramos
                continue

    except serial.SerialException as e:
        print(f"No se pudo conectar al Arduino: {e}")


##SerialArduino = serial.Serial(arduino_port, 9600)
##ime.sleep(1)

##while 1:
##    cad = SerialArduino.readline()
##    print(cad)


