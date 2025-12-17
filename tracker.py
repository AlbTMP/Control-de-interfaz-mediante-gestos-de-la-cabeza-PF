import re

class Traker:
    
    

    def get_variables2(self, data_bytes):
        
        
        data_str = data_bytes.encode(errors='ignore').strip()
        print(data_str)
        
        if not data_str:
            raise ValueError("La entrada está vacía.")
    
    
        numeros = re.findall(r"-?\d+\.\d+|-?\d+", data_str)
    
        
        if len(numeros) != 6:
            raise ValueError(f"No se encontraron numeros")
    
       
        return tuple(float(n) for n in numeros)


    """
    def convertir_serial(cadena):
        valores = []
        # Separar por comas
        partes = cadena.split(",")

        for p in partes:
            p = p.strip()  # quitar espacios
            try:
                # Intentar convertir a float
                num = float(p)
                valores.append(num)
            except ValueError:
                # Si no se puede convertir (texto), se ignora
                continue

            # Detenerse cuando ya tengamos 7 valores
            if len(valores) == 7:
                break

        # Verificar que se obtuvieron 7 valores
        if len(valores) != 7:
            raise ValueError("No se encontraron 7 valores numéricos válidos")

        # Asignar a variables
        v1, v2, v3, v4, v5, v6, v7 = valores
        return v1, v2, v3, v4, v5, v6, v7

    """

    def procesar_entrada_serial(self, data_bytes):
        
        if isinstance(data_bytes, bytes):
            data_str = data_bytes.encode(errors='ignore').strip()
        else:
            data_str = data_bytes.strip()  #

        #data_str = data_bytes.decode(errors='ignore').strip()
        #print(data_str)
        
        partes = [p.strip() for p in data_str.split(",")]

        if len(partes) < 7:
            print("n")#return None  

        try:
            
            v1 = float(partes[0])
            v2 = float(partes[1])
            v3 = float(partes[2])
            v4 = float(partes[3])
            v5 = float(partes[4])
            v6 = float(partes[5])

            #texto
            v7 = partes[6].strip('"')

            return v1, v2, v3, v4, v5, v6, v7

        except ValueError:
            print("valio madres")
            return None