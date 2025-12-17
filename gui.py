import tkinter as tk
import math
import random
from enum import Enum, auto

class _State(Enum):
    IN_4           = auto()
    WAIT_CENTER_4  = auto()
    IN_8           = auto()
    WAIT_CENTER_8  = auto()

class FloatingRadialUI:
    def __init__(self, root):
        self.root = root



        self.accionar = "non"

       




        self.radius = 45
        self.circle_r = 30
        self.offset = 40
        self.deadzone = 5
        self.threshold = 15

        self.labels = ["  V    ()    Y  \n  O           E\n  G    A    H",
                        "  .    U    ,  \n  T           L\n  :    C    #",
                          "  x    d    k  \n  b           m\n  w    p    ñ",
                          "  q    r    f  \n  i           s\n  z    n    j"]  
        
        self.labels2 = ["  V    ()    Y  \n  O           E\n  G    A    H",
                        "  .    U    ,  \n  T           L\n  :    C    #",
                          "  x    d    k  \n  b           m\n  w    p    ñ",
                          "  q    r    f  \n  i           s\n  z    n    j",
                          "  V    ()    Y  \n  O           E\n  G    A    H",
                        "  .    U    ,  \n  T           L\n  :    C    #",
                          "  x    d    k  \n  b           m\n  w    p    ñ",
                          "  q    r    f  \n  i           s\n  z    n    j"]  
        

        ####################################
        self.group_chars = [
            #"e","y","()","v","o","g","a","h"
            #v","()","y","o","e","g","a","h
            ["()","Y","o","e","g","a","h","v"],   # sector 0 (abajo)
            ["u",",","t","l",":","c","#","."],   # sector 1 (izq)
            ["d","k","b","m","w","p","ñ","x"],   # sector 2 (arriba)
            ["r","f","i","s","z","n","j","q"]    # sector 3 (der)
        ]
        ######################################




        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        #self.win.attributes("-alpha", 0.85)
        self.win.attributes("-transparentcolor", "white")

        self.win.attributes("-alpha", 0.60)  #0.4

        self.canvas = tk.Canvas(self.win, width=200, height=200,
                                 bg="white", highlightthickness=0)
        self.canvas.pack()

        self.items = []
        self.texts = []
        



         ##############
        #self.state = 4                     # 4 or 8
        self.highlight_index = None        # sector actual
        self.stable_frames = 0             # contador para confirmar selección
        self.FRAMES_TO_CONFIRM = 5         # ajusta 50 ms * 5 = 250 ms
        #self.draw_menu()                   # dibuja 4 inicialmente


        self.state        = _State.IN_4
        self.center_frames = 0          # frames seguidos en dead-zone
        self.CENTER_FRAMES_NEEDED = 4   # 4·50 ms = 200 ms
        #################




        self.draw_menu()
        self.follow_mouse()

        # simulación de entrada MPU
        self.pitch = 0
        self.yaw = 0
        self.update_from_mpu()
        self.win.withdraw()


        

    def draw_menu(self):

        
        cx, cy = 100, 100
        angles = [90, 0, 180, 270]

        for label, ang in zip(self.labels, angles):
            rad = math.radians(ang)
            x = cx + self.radius * math.cos(rad)
            y = cy - self.radius * math.sin(rad)

            circle = self.canvas.create_oval(
                x - self.circle_r, y - self.circle_r,
                x + self.circle_r, y + self.circle_r,
                fill="#FFFFFF", outline=""
            )

            text = self.canvas.create_text(
                x, y, text=label,
                fill="black",
                font=("Arial", 8, "bold")
            )

            self.items.append(circle)
            self.texts.append(text)

        # centro
        self.canvas.create_oval(
            cx - 8, cy - 8,
            cx + 8, cy + 8,
            fill="#555", outline=""
        )

    def highlight(self, index):
        for i, item in enumerate(self.items):
            color = "#FFD700" if i == index else "#3A9AD9"
            self.canvas.itemconfig(item, fill=color)

    def follow_mouse(self):
        x = self.root.winfo_pointerx()-150
        y = self.root.winfo_pointery()-150
        self.win.geometry(f"+{x + self.offset}+{y + self.offset}")
        self.root.after(16, self.follow_mouse)

    # 🔥 Integración MPU (aquí conectas tu serial)
    def update_from_mpu(self):

        #################################
        idx = self.direction_from_angles(self.pitch, self.yaw)
        in_center = (idx is None)

    # --------- gestión de “volver al centro” ---------
        if self.state in (_State.WAIT_CENTER_4, _State.WAIT_CENTER_8):
            if in_center:
                self.center_frames += 1
                if self.center_frames >= self.CENTER_FRAMES_NEEDED:
                    self.center_frames = 0
                    if self.state == _State.WAIT_CENTER_4:
                        self.expand_to_8()
                    else:  # WAIT_CENTER_8
                        self.collapse_to_4()
            else:
                self.center_frames = 0
            self.highlight(-1)
            self.root.after(50, self.update_from_mpu)
            return

        # --------- estados normales IN_4 / IN_8 ---------
        if in_center:
            self.stable_frames = 0
            self.highlight(-1)
        else:
            if idx == self.highlight_index:
                self.stable_frames += 1
                if self.stable_frames >= self.FRAMES_TO_CONFIRM:
                    self.select_current(idx)
            else:
                self.stable_frames = 0
                self.highlight_index = idx
                self.highlight(idx)

        self.root.after(50, self.update_from_mpu)
        ##################################################



        # ---- SIMULACIÓN ----
        #self.pitch = random.uniform(-30, 30)
        #self.yaw = random.uniform(-30, 30)
        # --------------------
        """
        index = self.direction_from_angles(self.pitch, self.yaw)
        if index is not None:
            self.highlight(index)
        else:
            self.highlight(-1)

        self.root.after(200, self.update_from_mpu)
        """


    # ---------- acción de entrar/salir ----------
    


    """
        if self.state == _State.IN_4:
            self.selected_sector = idx
            self.state = _State.WAIT_CENTER_4   # ← esperar centro
        elif self.state == _State.IN_8:
            self.key_action(idx)
            self.state = _State.WAIT_CENTER_8   # ← esperar centro
        """


    def key_action(self, idx8):
        sector = self.selected_sector
        char   = self.group_chars[sector][idx8]
        self.accionar = char
        print("KEY ->", char)
    # controles.send_key(char)   # cuando quieras integrarlo
    # controles.send_key(char)   # cuando quieras integrarlo




        """Aquí envías la tecla que corresponda al PCController"""
        # ejemplo: mapeo directo a una lista de strings
        #keys = ["a","b","c","d","e","f","g","h"]
        #print("KEY:", keys[idx8])
        # controles.send_key(keys[idx8])   # descomenta cuando tengas la instancia

    
    def direction_from_angles(self, pitch, yaw):
        """Devuelve índice 0-3 (4 sectores) o 0-7 (8 sectores) o None"""
        #############################
        dead = self.deadzone
        thr  = self.threshold
        #dead, thr = self.deadzone, self.threshold
        if abs(pitch) < dead and abs(yaw) < dead:
            return None


        if self.state == _State.IN_4:
            if pitch > thr:                 # mirar arriba
                return 1
            if pitch < -thr:                # mirar abajo
                return 2
            if yaw > thr:                   # mirar derecha
                return 3
            if yaw < -thr:                  # mirar izquierda
                return 0
            return None                     # dentro de dead-zone
        else:  # 8 sectores
            
            angle = math.degrees(math.atan2(-pitch, -yaw)) % 360
            sector = int((angle + 22.5) // 45) % 8
            return sector



        """
        if abs(pitch) < dead and abs(yaw) < dead:
            return None

        if self.state == 4:
            if abs(pitch) > abs(yaw):
                return 0 if pitch > thr else 1          # abajo / arriba
            else:
                return 3 if yaw > thr else 2            # derecha / izquierda
            
        
        else:  # 8 sectores
            
            angle = math.degrees(math.atan2(-pitch, yaw)) % 360
            sector = int((angle + 22.5) // 45) % 8
            return sector
        ##############################
        
        if pitch > 8.0:
            return 2
        
        if pitch < -8.0:
            return 1
        

        if yaw >3.0:
            return 0
        if yaw < -3.0:
            return 3
        if pitch < 7.0 and pitch > -8.0 or yaw < 7.0 and yaw > -7.0:
            return None
        """
    ############################
        """
        if abs(pitch) < self.deadzone and abs(yaw) < self.deadzone:
            return None

        if abs(pitch) > abs(yaw):
            return 0 if pitch > self.threshold else 3
        else:
            return 2 if yaw > self.threshold else 1
        """

    #========================= 8 CIRSULOS
    def draw_menu2(self):
        cx, cy = 100, 100  # Coordenadas del centro
        angles = [i * 45 for i in range(8)]  # Ángulos para 8 círculos, separados por 45°

        for label, ang in zip(self.labels, angles):
            rad = math.radians(ang)
            x = cx + self.radius * math.cos(rad)
            y = cy - self.radius * math.sin(rad)

            circle = self.canvas.create_oval(
                x - self.circle_r, y - self.circle_r,
                x + self.circle_r, y + self.circle_r,
                fill="#FFFFFF", outline=""
            )

            text = self.canvas.create_text(
                x, y, text=label,
                fill="black",
                font=("Arial", 8, "bold")
            )

            self.items.append(circle)
            self.texts.append(text)

        # Centro
        self.canvas.create_oval(
            cx - 8, cy - 8,
            cx + 8, cy + 8,
            fill="#555", outline=""
        )

        #===================NUEVOS

        # ---------- acción de entrar/salir ----------
    def select_current(self, idx):
        if self.state == _State.IN_4:
            if 0 <= idx <= 3:              # guarda solo si es válido
                self.selected_sector = idx
                self.state = _State.WAIT_CENTER_4
        elif self.state == _State.IN_8:
            self.key_action(idx)
            self.state = _State.WAIT_CENTER_8


    def collapse_to_4(self):
        self.canvas.delete("all")
        self.items.clear()
        self.texts.clear()
        self.state = _State.IN_4
        self.draw_menu()      # tu método original de 4
  



    def expand_to_8(self):
        sector4 = self.selected_sector
##############
        #angles = [(i * 45 + 90) % 360 for i in range(8)]
################
        self.canvas.delete("all")
        self.items.clear()
        self.texts.clear()
        self.state = _State.IN_8
        sector4 = self.selected_sector
        #print("ññññññaaaaaaaa",sector4)
        #if sector4 ==6:
        #    sector4=2
        #    self.selected_sector = 2

        #if sector4 ==4:
        #    sector4=3
        #    self.selected_sector = 3
        print("ññññññaaaaaaaa",sector4)
        chars = self.group_chars[sector4]   # ← letras correspondientes
        
        cx, cy = 100, 100
        angles = [(i * 45 + 90) % 360 for i in range(8)]
        for i, ang in enumerate(angles):
            
            rad = math.radians(ang)
            x = cx + self.radius * math.cos(rad)
            y = cy - self.radius * math.sin(rad)

            c = self.canvas.create_oval(
                x - self.circle_r, y - self.circle_r,
                x + self.circle_r, y + self.circle_r,
                fill="#FFFFFF", outline="")
            t = self.canvas.create_text(
                x, y, text=chars[i],   # ← letra única
                fill="black", font=("Arial", 10, "bold"))
            self.items.append(c)
            self.texts.append(t)

        # círculo central
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill="#555", outline="")
        

"""
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    ui = FloatingRadialUI(root)
    root.mainloop()
"""
#root = tk.Tk()
#root.withdraw()

#ui = FloatingRadialUI(root)
#root.mainloop()
