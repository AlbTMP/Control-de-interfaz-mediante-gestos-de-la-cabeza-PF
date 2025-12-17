import serial
import serial.tools.list_ports

import os
import time


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
    
    def autodetect_bluetooth_port():
        # Detectar puertos COM en Windows y /dev/rfcomm en Linux
        if os.name == 'nt':  # Si es Windows
            ports = [f'COM{i}' for i in range(1, 256)]
        else:  # Si es Linux o macOS
            ports = [f'/dev/ttyUSB{i}' for i in range(0, 5)]  # O puede ser /dev/rfcomm0
            ports += [f'/dev/ttyACM{i}' for i in range(0, 5)]

        # Intentar abrir cada puerto hasta encontrar el correcto
        for port in ports:
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                print(f"Puerto encontrado: {port}")
                return port #ser
            except serial.SerialException:
                continue
    
        print("No se pudo encontrar un puerto Bluetooth válido.")
        return None