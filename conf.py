import Serial
import serial.tools.list_ports

BAUD_RATE = 115200
MOUSE_SENS = 0.3


asalir = False


##suavizado
alpha = 0.01
sx, sy = 0, 0
deadzone = 100