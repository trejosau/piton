import json
from datetime import datetime


class Arreglo:
    def __init__(self):
        self.items = []

    def agregar(self, *items):
        for item in items:
            self.items.append(item)

    def eliminar(self, id):
        for i, elem in enumerate(self.items):
            if hasattr(elem, '__dict__') and elem.__dict__.get("id") == id:
                del self.items[i]
                return True
        return False

    def actualizar(self, id, clave, nuevo_valor):
        for elem in self.items:
            if hasattr(elem, '__dict__') and elem.__dict__.get("id") == id:
                if clave in elem.__dict__:
                    setattr(elem, clave, nuevo_valor)
                    return True
                return False
        return False

    def convADiccionarios(self):
        arreglo_convertido = []
        for item in self.items:
            # Si el objeto tiene el método convADiccionario, úsalo.
            if hasattr(item, 'convADiccionario'):
                diccionario = item.convADiccionario()
            elif isinstance(item, dict):
                diccionario = item
            else:
                diccionario = item.__dict__.copy()
                diccionario.pop('es_arreglo', None)
            # Anida los objetos complejos (maestro, alumnos, etc.)
            if 'maestro' in diccionario and diccionario['maestro'] is not None and hasattr(diccionario['maestro'],
                                                                                           'convADiccionario'):
                diccionario['maestro'] = diccionario['maestro'].convADiccionario()
            if 'alumnos' in diccionario and hasattr(diccionario['alumnos'], 'items'):
                diccionario['alumnos'] = [alumno.convADiccionario() for alumno in diccionario['alumnos'].items]
            arreglo_convertido.append(diccionario)
        return arreglo_convertido

    def mostrar_diccionario(self):
        if not self.items:
            print("No hay elementos")
        else:
            print(json.dumps(self.convADiccionarios(), indent=4, ensure_ascii=False))


    def __str__(self):
        if not self.items:
            return "No hay elementos"
        return str(len(self.items))
