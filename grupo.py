from alumno import Alumno
from arreglo import Arreglo
from maestro import Maestro


class Grupo(Arreglo):
    _id_counter = 1

    def __init__(self, nombre=None, maestro=None):
        if nombre is None and maestro is None:
            Arreglo.__init__(self)
            self.es_arreglo = True
        else:
            self.id = Grupo._id_counter
            Grupo._id_counter += 1
            self.nombre = nombre
            self.maestro = maestro
            self.alumnos = Alumno()
            self.es_arreglo = False

    def asignar_maestro(self, maestro):
        self.maestro = maestro

    def cambiarNombre(self, nombre):
        self.nombre = nombre

    def __str__(self):
        if self.es_arreglo:
            return Arreglo.__str__(self)

        maestro_info = f"{self.maestro.nombre} {self.maestro.apellido}" if self.maestro else "Falta asignar"

        return (
            f"Grupo: {self.nombre}\n"
            f"Maestro: {maestro_info}\n"
            f"Total de alumnos: {str(self.alumnos)}\n"
        )


if __name__ == "__main__":
    a1 = Alumno("Alberto", "Trejo", 18, 23170093, 10)
    a2 = Alumno("Jesus", "De la rosa", 19, 23170119, 10)
    m1 = Maestro("Ramiro", "Esquivel", 40, "1", "Android")
    grupo_mobile = Grupo("Desarrollo Móvil", Maestro("Ramiro", "Esquivel", 40, "1", "Android"))

    grupo_mobile.alumnos.agregar(a1, a2)
    grupo_mobile.asignar_maestro(m1)

    grupo_mobile.alumnos.actualizar(a1, 'promedio', 5)


    grupos_mobile = Grupo()
    grupos_mobile.agregar(grupo_mobile, grupo_mobile, grupo_mobile, grupo_mobile)
    grupos_mobile.eliminar(grupo_mobile.id)

    print(grupos_mobile)
