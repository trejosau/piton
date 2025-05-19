import json

from arreglo import Arreglo


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
            return None
        diccionario = self.__dict__.copy()
        diccionario.pop('es_arreglo', None)
        return diccionario

    def imprimir_diccionario(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

    def cambiarEspecialidad(self, especialidad):
        self.especialidad = especialidad

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
    m2.imprimir_diccionario()

    maestros = Maestro()
    maestros.agregar(m1)
    maestros.eliminar(m1.id)
    maestros.agregar(m2)
    maestros.agregar(m3)
    maestros.mostrar_diccionario()
