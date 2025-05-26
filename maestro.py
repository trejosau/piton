import json

from arreglo import Arreglo

def leerJson(archivo):
    import json
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def instanciar_maestros(archivo):

    datos = leerJson(archivo)
    if isinstance(datos, list):
        arreglo = Maestro()
        for d in datos:
            maestro = Maestro(
                nombre=d.get("nombre"),
                apellido=d.get("apellido"),
                edad=d.get("edad"),
                num_maestro=d.get("num_maestro"),
                especialidad=d.get("especialidad")
            )
            arreglo.agregar(maestro)
        return arreglo
    elif isinstance(datos, dict):
        return Maestro(
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido"),
            edad=datos.get("edad"),
            num_maestro=datos.get("num_maestro"),
            especialidad=datos.get("especialidad")
        )
    else:
        print("Formato de JSON no reconocido")
        return None


class Maestro(Arreglo):
    _id_counter = 1

    def __init__(self, nombre=None, apellido=None, edad=None, num_maestro=None, especialidad=None):
        if nombre is None and apellido is None and edad is None and num_maestro is None and especialidad is None:
            Arreglo.__init__(self)
            self.es_arreglo = True
        else:
            self.id = Maestro._id_counter
            Maestro._id_counter += 1
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.num_maestro = num_maestro
            self.especialidad = especialidad
            self.es_arreglo = False

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
    m1 = Maestro("Ramiro", "Esquivel", 40, "1", "Android")
    m2 = Maestro("Jesus", "Burciaga", 40, "2", "iOS")
    m3 = Maestro("Daniel", "Garcia", 19, "3", "MongoDB")
    print(m1)

    maestros = Maestro()
    maestros.agregar(m1)
    maestros.eliminar(m1.id)
    maestros.agregar(m2)
    maestros.agregar(m3)

    maestros.guardar_como_json()

    maestrosDesdeJson = instanciar_maestros("Maestro.json")

    m4 = Maestro("Nuevo", "Maestro", 30, "4", "Python")
    maestrosDesdeJson.agregar(m4)

    maestrosDesdeJson.mostrar_diccionario()
