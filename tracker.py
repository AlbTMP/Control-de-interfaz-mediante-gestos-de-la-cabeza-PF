import re

class Traker:
    
    def get_variables(self, data_bytes):
        data_str = data_bytes.strip()
        numeros = re.findall(r"-?\d+\.?\d*", data_str)
        if len(numeros) != 6:
            raise ValueError(f"No se encontraron exactamente dos números en: {data_str}")
        return tuple(float(n) for n in numeros)
    def get_variables2(self, data_bytes):
        # Limpiar y separar en líneas
        
        data_str = data_bytes.encode(errors='ignore').strip()
        print(data_str)
        # Si hay líneas vacías o de texto, las ignoramos
        if not data_str:
            raise ValueError("La entrada está vacía.")
    
        # Buscar todos los números decimales, incluyendo negativos y con decimales
        numeros = re.findall(r"-?\d+\.\d+|-?\d+", data_str)
    
        # Comprobar que haya exactamente 6 números
        if len(numeros) != 6:
            raise ValueError(f"No se encontraron exactamente 6 números en: {data_str}")
    
        # Convertirlos a flotantes y devolverlos como tupla
        return tuple(float(n) for n in numeros)
