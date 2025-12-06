import pynput
from pynput.mouse import Controller
from pynput.keyboard import Listener, Key
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController, Key

from conf import *
import time

SENS      = 2.0        # píxeles por unidad que llega
ACCEL     = 1.15       # exponencial: cuanto más inclinación, más rápido
ZONA_MUERTA = 30

click_in_progress = False
class PCController:
    def __init__(self, sensibilidad_mouse):
        self.mouse = Controller()
        self.tecladoIN = Listener()
        self.tecladoOU = KeyboardController()
        self.mouse_sen = sensibilidad_mouse

    def salir(self):
        ini = self.tecladoIN = Listener(on_press= self.on_press)
        return ini


    def centrar():
        self.mouse.position = (1280/2, 720/2)

    def mover_mouse(self, gz, gx, gy):
        gz*=180
        gx*=180
        ox, oy = self.mouse.position
        gz, gx = self.suavizar_movimiento(gx,gz,ox,oy)
        if gy<5 and gy > -5:
            self.mouse.position = (gx, gz)
        
          
    def clicks_mouse(self, gy):
        global click_in_progress
        if not click_in_progress:
            click_in_progress = True
            if (gy > 8):
                self.mouse.click(Button.left, 1)
                time.sleep(1)

        #time.sleep(1)
           
            if (gy < -8):
                self.mouse.click(Button.right, 1)
                time.sleep(1)
            click_in_progress = False
          




    def on_press(key):
        global salir
        if key == Key.esc:
            print("Tecla ESC presionada. Saliendo...")
            salir = True
            return False  # Detiene el listener
        
    def suavizar_movimiento(self,x, y, last_x, last_y):
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
    


    def mueve_mouse(self, gz, gx, gy):
        
        dx=gz
        dy=gx
        # Zona muerta
        if abs(dx) < ZONA_MUERTA: dx = 0
        if abs(dy) < ZONA_MUERTA: dy = 0

        # Aceleración exponencial suave
        dx = (dx ** (ACCEL if dx > 0 else -ACCEL)) / (30 ** (ACCEL - 1))
        dy = (dy ** (ACCEL if dy > 0 else -ACCEL)) / (30 ** (ACCEL - 1))

        # Píxeles finales
        mx = int(dx * SENS)
        my = int(dy * SENS)

        # Mover (pyautogui ya frena los bordes de pantalla)
        if gy<5 and gy > -5:
            self.mouse.position = (mx, my)
        
        #pyautogui.moveRel(mx, my)

        #return mx, my


        
