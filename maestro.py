from arreglo import Arreglo


class Maestro(Arreglo):
    def __init__(self, nombre=None, apellido=None, edad=None, num_maestro=None, especialidad=None):
        if nombre is None and apellido is None and edad is None and num_maestro is None and especialidad is None:
            Arreglo.__init__(self)
            self.es_arreglo = True
        else:
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.num_maestro = num_maestro
            self.especialidad = especialidad
            self.es_arreglo = False

    def __str__(self):
        if self.es_arreglo:
            return Arreglo.__str__(self)
        return (f"Maestro: {self.nombre} {self.apellido}, {self.edad} años, "
                f"ID: {self.num_maestro}, Especialidad: {self.especialidad}")

    def cambiarEspecialidad(self, especialidad):
        self.especialidad = especialidad


if __name__ == "__main__":
    m1 = Maestro("Ramiro", "Esquivel", 40, "1", "Android")
    m2 = Maestro("Jesus", "Burciaga", 40, "2", "iOS")
    print(m1)


    print(m2)
    maestros = Maestro()
    maestros.agregar(m1)
    maestros.eliminar(m1)
    maestros.agregar(m2)
    print(maestros)
