import json
from arreglo import Arreglo

class Maestro(Arreglo):
    def __init__(self, nombre=None, apellido=None, edad=None, num_maestro=None, especialidad=None, **kwargs):
        if nombre is None and apellido is None and edad is None and num_maestro is None and especialidad is None:
            # Arreglo de maestros
            Arreglo.__init__(self)
            self.es_arreglo = True
        else:
            # Instancia individual de maestro
            self.id = num_maestro
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.num_maestro = num_maestro
            self.especialidad = especialidad
            self.es_arreglo = False

    def leerJson(self, archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    def instanciar(self, entrada):
        if isinstance(entrada, str):
            datos = self.leerJson(entrada)
        else:
            datos = entrada

        self.items.clear()
        if isinstance(datos, list):
            for d in datos:
                maestro = Maestro(**d)
                self.agregar(maestro)
        elif isinstance(datos, dict):
            maestro = Maestro(**datos)
            self.agregar(maestro)
        else:
            print("Formato de JSON no reconocido")

    def convADiccionario(self):
        if self.es_arreglo:
            return self.convADiccionarios()
        diccionario = self.__dict__.copy()
        diccionario.pop('es_arreglo', None)
        return diccionario

    def getDict(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

    def cambiarEspecialidad(self, especialidad):
        self.especialidad = especialidad

    def guardar_como_json(self):
        clase = self.__class__.__name__
        nombre_archivo = f"{clase}.json"
        datos = self.convADiccionario()
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print(f"Archivo actualizado como {nombre_archivo}")

    def __str__(self):
        if self.es_arreglo:
            return Arreglo.__str__(self)
        return (f"Maestro: {self.nombre} {self.apellido}, {self.edad} años, "
                f"ID: {self.num_maestro}, Especialidad: {self.especialidad}")


if __name__ == "__main__":
    # Crear y guardar maestros
    m1 = Maestro("Ramiro", "Esquivel", 40, "1", "Android")
    m2 = Maestro("Jesus", "Burciaga", 40, "2", "iOS")
    m3 = Maestro("Daniel", "Garcia", 19, "3", "MongoDB")

    maestros = Maestro()
    maestros.agregar(m1)
    maestros.agregar(m2)
    maestros.agregar(m3)
    maestros.eliminar("1")  # Elimina por num_maestro (que ahora es el id)

    maestros.guardar_como_json()

    # Instanciar desde archivo
    maestrosDesdeJson = Maestro()
    maestrosDesdeJson.instanciar("Maestro.json")

    # Agregar uno nuevo
    m4 = Maestro("Nuevo", "Maestro", 30, "4", "Python")
    maestrosDesdeJson.agregar(m4)

    # Mostrar en formato JSON serializable
    maestrosDesdeJson.mostrar_diccionario()
