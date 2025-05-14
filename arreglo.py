import json


class Arreglo:
    def __init__(self):
        self.items = []

    def agregar(self, *items):
        for item in items:
            diccionario = item.__dict__.copy()
            diccionario.pop('es_arreglo', None)

            if 'maestro' in diccionario and hasattr(diccionario['maestro'], '__dict__'):
                maestro_obj = diccionario['maestro']
                maestro_dict = maestro_obj.__dict__.copy()
                maestro_dict.pop('es_arreglo', None)
                diccionario['maestro'] = maestro_dict

            if 'alumnos' in diccionario and hasattr(diccionario['alumnos'], 'items'):
                diccionario['alumnos'] = diccionario['alumnos'].items

            self.items.append(diccionario)

    def eliminar(self, id):
        for i, elem in enumerate(self.items):
            if elem.get("id") == id:
                del self.items[i]
                return True
        return False

    def actualizar(self, id, clave, nuevo_valor):
        for elem in self.items:
            if elem.get("id") == id:
                if clave in elem:
                    elem[clave] = nuevo_valor
                    return True
                return False
        return False

    def __str__(self):
        if not self.items:
            return "No hay elementos"
        return json.dumps(self.items, indent=4, ensure_ascii=False)

