import serial
import serial.tools.list_ports

class SerialRead:
    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud, timeout=1)

    def read_data(self):
        try:
            line = self.ser.readline().decode().strip()
            return line
        except:
            return None
    
    def find_arduino():
        """Busca el puerto donde está conectado Arduino."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Arduino suele tener 'Arduino' en la descripción o un VID/PID conocido
            if 'Arduino' in port.description or 'ttyACM' in port.device or 'ttyUSB' in port.device:
                return port.device
        return None