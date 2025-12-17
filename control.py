import pynput
from pynput.mouse import Controller
from pynput.keyboard import Listener, Key
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController, Key


from pynput.keyboard import Controller as KeyboardController

import math
#import uiautomation as auto

from screeninfo import get_monitors

from conf import *
import time



SENS_BASE   = 5.0       
ZONA_MUERTA = 1.0      
ACEL_EXP   = 3.7       
MAX_ANG     = 30.0      

#SENS      = 2.0        
#ACEL     = 1.15      
#ZONA_MUERTA = 30

click_in_progress = False
class PCController:
    def __init__(self, sensibilidad_mouse):
        self.mouse = Controller()
        self.tecladoIN = Listener()
        self.tecladoOU = KeyboardController()
        self.mouse_sen = sensibilidad_mouse
        self.monitor = get_monitors()
        #click
        self.roll_prev   = 0
        self.click_state = 0          # 0=quieto, 1=ladeo detectado
        self.dead        = 4          # ° dentro de “recto”
        self.thr         = 8             # ° para activar
        self.keyboard = KeyboardController()



    def salir(self):
        ini = self.tecladoIN = Listener(on_press= self.on_press)
        return ini


    def centrar(self):
        

        monitor = self.monitor[0]#monitors[0]
        ancho = monitor.width#win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        alto  = monitor.height#win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.mouse.position = (ancho/2, alto/2)
       


    def mover_mouse(self, gz, gx, gy):
        gz*=180
        gx*=180
        ox, oy = self.mouse.position
        gz, gx = self.suavizar_movimiento(gx,gz,ox,oy)
        if gy<5 and gy > -5:
            self.mouse.position = (gx, gz)
        
          
    def clicks_mouse_p1(self, gy):
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
    
    def clicks_mouse_p2(self, roll):
        """
        roll: valor instantáneo de roll (gy en tu código)
        """
        # ----- paso 1: oreja-hombro -----
        if self.click_state == 0:
            if roll > self.thr:               # ladeo derecho
                self.click_side = 'left'
                self.click_state = 1
            elif roll < -self.thr:            # ladeo izquierdo
                self.click_side = 'right'
                self.click_state = 1
            return

        # ----- paso 2: vuelta al centro -----
        if self.click_state == 1:
            if abs(roll) < self.dead:         # cabeza recta
                if self.click_side == 'left':
                    self.mouse.click(Button.left, 1)
                else:
                    self.mouse.click(Button.right, 1)
                self.click_state = 0          # reinicia máquina




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
    

    """
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
    """

    def detectar_palabra_en_serial(self, palabra_objetivo):
        if "clic" in palabra_objetivo:
            self.mouse.click(Button.left, 1)
        if "anticlic" in palabra_objetivo:
            self.mouse.click(Button.right, 1)
    

    def escribir_letra(self,letra):
        if letra == "borrar":
            
            self.keyboard.press(Key.backspace)
            self.keyboard.release(Key.backspace)

        else:
            self.tecladoOU.type(letra)

    def get_mouse_y(self):
        return self.mouse.position[1]

    def move_rel(self, dx, dy):
        
        # pos actual
        x, y = self.mouse.position
    
        # tamaño de la pantalla 
        ancho = 1280
        alto  = 720
        
        x = max(0, min(ancho - 1, x + dx))
        y = max(0, min(alto  - 1, y + dy))
    
        self.mouse.position = (int(x), int(y))
        

    def move_rel2(self, dx, dy) -> None:
       
       
        if abs(dx) < ZONA_MUERTA:
            dx = 0
        else:
            dx -= math.copysign(ZONA_MUERTA, dx)   

        if abs(dy) < ZONA_MUERTA:
            dy = 0
        else:
            dy -= math.copysign(ZONA_MUERTA, dy)

        
        def exp_curve(v):
            if v == 0:
                return 0
            sign = 1 if v > 0 else -1
            v = min(abs(v), MAX_ANG)              
            return sign * (v ** ACEL_EXP) / (MAX_ANG ** (ACEL_EXP - 1))

        dx = exp_curve(dx)
        dy = exp_curve(dy)

        # limites
        mx = int(dx * SENS_BASE)
        my = int(dy * SENS_BASE)

       
        x, y = self.mouse.position
        
        monitor = self.monitor[0]#monitors[0]
        ancho = monitor.width #win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        alto  = monitor.height #win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
       

        x = max(0, min(ancho - 1, x + mx))
        y = max(0, min(alto  - 1, y + my))
        self.mouse.position = (x, y)



        ##-------------------
"""

    def usuario_entro_en_campo_texto(timeout=5, intervalo=0.2):
        

        

        inicio = time.time()
        ultimo_control = None

        while time.time() - inicio < timeout:
            control = auto.GetFocusedControl()

            if control and control != ultimo_control:
                ultimo_control = control

                if (
                    control.ControlType == auto.ControlType.EditControl
                    or control.GetPattern(auto.PatternId.ValuePattern)
                ):
                    return True

            time.sleep(intervalo)

        return False
            

"""