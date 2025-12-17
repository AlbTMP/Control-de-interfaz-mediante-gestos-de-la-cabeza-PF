import queue
from Serial import SerialRead
from tracker import Traker
from control import PCController
#from gui import BurbujaMouse
from conf import *
from pynput.keyboard import Listener, Key
import threading
import time
import tkinter as tk
from gui import FloatingRadialUI



# --- Estado para activar el teclado ---
abajo_inicio = None  # timestamp cuando se inclinó hacia abajo
esperando_volver = False
INTERFAZ_ACTIVA = False
UMBRAL_ABAJO = 12  # grados de inclinación hacia abajo
TIEMPO_ABAJO = 6.0  # segundos



mpu_data = {'x': 0, 'y': 0, 'z': 0, 'a': 0, 'b': 0, 'c': 0, 'm': "non"}
mpu_data_lock = threading.Lock()
salir = False


ARDUINO_PORT = SerialRead.find_arduino()
if ARDUINO_PORT is None:
    ARDUINO_PORT=SerialRead.autodetect_bluetooth_port()
    print(ARDUINO_PORT)





root = tk.Tk()
#root.geometry("400x300")
#root.title("Tooltip que sigue al mouse")

root.withdraw()
ui = FloatingRadialUI(root)
ALTO_PANTALLA = root.winfo_screenheight()



serial = SerialRead(ARDUINO_PORT,BAUD_RATE)
tracker = Traker()
controles = PCController(3)
#interfaz = BurbujaMouse(root, "rotar derecha para activar teclado")


#root.mainloop()



def on_press(key):
    global salir
    if key == Key.esc:
        print("Tecla ESC presionada. Saliendo...")
        salir = True
        return False  # Detiene el listener
### bucle- whil

def leer_mpu(cad):
    #print("awebo",cad)
    cad = serial.read_data()
    try:

        #x, y , z, a,b , c, m = tracker.get_variables2(cad)
        x, y , z, a,b , c, m = tracker.procesar_entrada_serial(cad)
        #print("aña",x,y,z, a, b, c, m)
        #controles.mover_mouse(x,z,y)

        with mpu_data_lock:
            mpu_data['x'] = x
            mpu_data['y'] = y
            mpu_data['z'] = z
            mpu_data['a'] = a
            mpu_data['b'] = b
            mpu_data['c'] = c
            mpu_data['m'] = m


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
                    #if controles.usuario_entro_en_campo_texto():

                     #   root.mainloop()
                    leer_mpu(cad)
                    #x, y , z, a,b , c,m= tracker.procesar_entrada_serial(cad)#get_variables(cad)
                   # print("aña",x,y,z, a, b, c)
                    #with mpu_data_lock:
                      #  mpu_data['x'] = x
                      #  mpu_data['y'] = y
                      #  mpu_data['z'] = z
                      #  mpu_data['a'] = a
                      #  mpu_data['b'] = b
                      #  mpu_data['c'] = c
                       # mpu_data['m'] = m


                    with mpu_data_lock:
                       x, y , z, a,b , c ,m= mpu_data['x'],mpu_data['y'],mpu_data['z'], mpu_data['a'],mpu_data['b'], mpu_data['c'],  mpu_data['m']


                    #x, y , z, a,b , c= tracker.get_variables(cad)
                    print("entradas",x,y,z, a, b, c,m)
                    if INTERFAZ_ACTIVA :
                        controles.centrar()
                    else:
                        controles.move_rel2(x,z)#mover_mouse(x,z,y)
                    #ui.direction_from_angles(x,z)
                        controles.clicks_mouse_p2(y)



                    #controles.detectar_palabra_en_serial(m)jz




                    if salir == True:
                        root.quit()
                        root.destroy()
                    

                except ValueError:
                # Si la línea no tiene 2 números, simplemente la ignoramos
                    continue

        except serial.SerialException as e:
            print(f"No se pudo conectar al Arduino: {e}")



hilo_clic = threading.Thread(target=bucle_1,daemon=True)
hilo_clic.start()






#===================================================
def update_gui():

    global abajo_inicio, esperando_volver, INTERFAZ_ACTIVA

    try:
        with mpu_data_lock:
            pitch = mpu_data['x']
            yaw = mpu_data['z']
            y = mpu_data['y']

        ui.pitch = pitch
        ui.yaw = yaw

        # --- Lógica de activación ---
        if not INTERFAZ_ACTIVA:
            if yaw > UMBRAL_ABAJO and abajo_inicio is None:
                abajo_inicio = time.time()

            elif yaw > UMBRAL_ABAJO and abajo_inicio is not None:
                if time.time() - abajo_inicio >= TIEMPO_ABAJO:
                    esperando_volver = True
                    abajo_inicio = None

            elif esperando_volver and abs(yaw) < 5:  # volvió a 0°
                ###################para dimension de pantalla
                
                # ----------------------------------------------
                INTERFAZ_ACTIVA = True
                esperando_volver = False
                ui.win.deiconify()  # Muestra la interfaz
                print("[INFO] Interfaz activada.")
                controles.centrar()

        else:
            # Si la interfaz está activa, actualiza el highlightz
            ui.direction_from_angles(pitch, yaw)
            if ui.accionar != "non":
                controles.escribir_letra(ui.accionar)
                ui.accionar ="non"

            # cerrar 
            if y < -12:
                INTERFAZ_ACTIVA = False
                ui.win.withdraw()
                print("[INFO] Interfaz cerrada.")
            
            # --- Borrar con roll derecho ---
            #if not INTERFAZ_ACTIVA and roll > 
            if y > 12:  # ajusta el umbral
                controles.escribir_letra("borrar")  # o usa controles.send_key(Key.backspace)

    except Exception as e:
        print("Error en update_gui:", e)

    root.after(50, update_gui)







"""

    try:
        with mpu_data_lock:
            pitch=mpu_data['x']
            yaw = mpu_data['z']
        
        ui.pitch = pitch
        ui.yaw   = yaw
        ui.direction_from_angles(pitch, yaw)   # actualiza highlight
        
        if ui.accionar=="non":
            controles.escribir_letra(ui.accionar)
    except queue.Empty:
        pass
    root.after(50, update_gui)   # 20 Hz es suficiente
"""

# ---------- arranque ----------
update_gui()      # primera llamada

root.deiconify()
root.mainloop()
#if salir == True:
#    root.quit()

"""
try:
    root.mainloop()   # Esto mantiene la GUI en ejecución, sin bloquear la lectura serial
except KeyboardInterrupt:
    print("Interrupción detectada, cerrando el programa.")
    salir = True
    root.quit()  # Salir de Tkinter de forma ordenada
#root.mainloop()   # <-- SIEMPRE en el hilo principal

try:
    root.deiconify()  # Muestra la ventana de la GUI
    root.mainloop()   # Esto mantiene la GUI en ejecución, sin bloquear la lectura serial
except Exception as e:
    print(f"Error en Tkinter: {e}")
finally:
    # Asegúrate de cerrar cualquier recurso y detener hilos al salir
    print("Cerrando el programa...")

    # Paramos todos los hilos de manera segura
    Salir = True
    hilo_mouse.join()  # Espera a que termine el hilo de lectura de datos
    hilo_clic.join()   # Espera a que termine el hilo de clics

    # Cierra la interfaz gráfica de manera ordenada
    root.quit()
    root.destroy()
    """