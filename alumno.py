from arreglo import Arreglo

class Alumno(Arreglo):
    def __init__(self, nombre=None, apellido=None, edad=None, matricula=None, promedio=None):
        if nombre is None and apellido is None and edad is None and matricula is None and promedio is None:
            Arreglo.__init__(self)
            self.es_arreglo = True
        else:
            self.id = matricula
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.matricula = matricula
            self.promedio = promedio
            self.es_arreglo = False

    def actualizarPromedio(self, promedio):
        self.promedio = promedio

    def __str__(self):
        if self.es_arreglo:
            return Arreglo.__str__(self)
        diccionario = self.__dict__.copy()
        diccionario.pop('es_arreglo', None)
        return str(diccionario)



if __name__ == "__main__":
    a1 = Alumno("Alberto", "Trejo", 18, 23170093, 10)
    print(a1)

    a2 = Alumno("Jesus", "De la rosa", 19, 23170119, 10)
    a2.actualizarPromedio(9.3)
    print(a2)

    alumnos = Alumno()
    alumnos.agregar(a1)
    alumnos.agregar(a2)
    alumnos.agregar(Alumno("Saul", "Sanchez", 20, 23170000, 10))
    alumnos.eliminar(23170093)
    print(alumnos)