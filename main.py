from Serial import SerialRead
from tracker import Traker
from control import PCController
from conf import *
from pynput.keyboard import Listener, Key
import threading
import time

mpu_data = {'x': 0, 'y': 0, 'z': 0, 'a': 0, 'b': 0, 'c': 0}
mpu_data_lock = threading.Lock()
salir = False


ARDUINO_PORT = SerialRead.find_arduino()
serial = SerialRead(ARDUINO_PORT,BAUD_RATE)
tracker = Traker()
controles = PCController(3)

def on_press(key):
    global salir
    if key == Key.esc:
        print("Tecla ESC presionada. Saliendo...")
        salir = True
        return False  # Detiene el listener
### bucle- whil

def leer_mpu(cad):
    print("awebo",cad)
    #cad = serial.read_data()
    try:

        x, y , z, a,b , c= tracker.get_variables2(cad)
        print("aña",x,y,z, a, b, c)
        controles.mover_mouse(x,z,y)

        with mpu_data_lock:
            mpu_data['x'] = x
            mpu_data['y'] = y
            mpu_data['z'] = z
            mpu_data['a'] = a
            mpu_data['b'] = b
            mpu_data['c'] = c


    except ValueError:
        print(e)


def bucle_1():
    global salir
    if ARDUINO_PORT is None and salir == False:
        print("No se encontró ningún Arduino conectado.")
        salir=True
    else:
        print(f"Arduino encontrado en: {ARDUINO_PORT}")
        # Conectar al Arduino
        try:
            #apagar = controles.salir()
            #apagar.start()
            print("Leyendo datos del Arduino (CTRL+C para salir)...")


            keyboard_listener = Listener(on_press=on_press)
            keyboard_listener.start()

            controles.centrar

            while not salir:
                cad = serial.read_data()
                if not cad:  # ignorar líneas vacías
                       continue
                try:
                    #leer_mpu(cad)
                    x, y , z, a,b , c= tracker.get_variables(cad)
                    print("aña",x,y,z, a, b, c)
                    with mpu_data_lock:
                        mpu_data['x'] = x
                        mpu_data['y'] = y
                        mpu_data['z'] = z
                        mpu_data['a'] = a
                        mpu_data['b'] = b
                        mpu_data['c'] = c


                    #with mpu_data_lock:
                     #   x, y , z, a,b , c = mpu_data['x'],mpu_data['y'],mpu_data['y'], mpu_data['a'],mpu_data['b'], mpu_data['c']


                    #x, y , z, a,b , c= tracker.get_variables(cad)
                    #print("aña",x,y,z, a, b, c)
                    controles.mover_mouse(x,z,y)

                except ValueError:
                # Si la línea no tiene 2 números, simplemente la ignoramos
                    continue

        except serial.SerialException as e:
            print(f"No se pudo conectar al Arduino: {e}")

def bucle_2():
    global salir
    while salir==False:
        with mpu_data_lock:
            y=mpu_data['y']
        print(y)
        controles.clicks_mouse(y)  # Llamada para hacer clic
        time.sleep(3)


hilo_mouse = threading.Thread(target=bucle_1)
hilo_clic = threading.Thread(target=bucle_2)


hilo_mouse.start()
hilo_clic.start()