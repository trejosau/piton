import json
from arreglo import Arreglo

def leerJson(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def instanciar_alumnos(archivo):

    datos = leerJson(archivo)

    if isinstance(datos, list):
        arreglo = Alumno()
        for d in datos:
            alumno = Alumno(
                nombre=d.get("nombre"),
                apellido=d.get("apellido"),
                edad=d.get("edad"),
                matricula=d.get("matricula"),
                promedio=d.get("promedio")
            )
            arreglo.agregar(alumno)
        return arreglo
    elif isinstance(datos, dict):
        return Alumno(
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido"),
            edad=datos.get("edad"),
            matricula=datos.get("matricula"),
            promedio=datos.get("promedio")
        )
    else:
        print("Formato de JSON no reconocido")
        return None



class Alumno(Arreglo):
    def __init__(self, nombre=None, apellido=None, edad=None, matricula=None, promedio=None, **kwargs):
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

    def guardar_como_json(self):
        clase = self.__class__.__name__
        nombre_archivo = f"{clase}.json"

        datos = self.convADiccionario()

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print(f"Archivo actualizado como {nombre_archivo}")

    def __str__(self):
        if getattr(self, 'es_arreglo', False):

            return Arreglo.__str__(self)
        else:
            return (
                f"Alumno: {self.nombre} {self.apellido}\n"
                f"Edad: {self.edad}\n"
                f"Matrícula: {self.matricula}\n"
                f"Promedio: {self.promedio}"
            )


    def actualizarPromedio(self, promedio):
        self.promedio = promedio

    def convADiccionario(self):
        if self.es_arreglo:
            return self.convADiccionarios()
        diccionario = self.__dict__.copy()
        diccionario.pop('es_arreglo', None)
        return diccionario

    def getDict(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

if __name__ == "__main__":
    a1 = Alumno("Alberto", "Trejo", 18, 23170093, 10)

    a2 = Alumno("Jesus", "De la rosa", 19, 23170119, 10)
    a2.actualizarPromedio(9.3)



    alumnos = Alumno()
    alumnos.agregar(a1)
    alumnos.agregar(a2)
    alumnos.agregar(Alumno("Saul", "Sanchez", 20, 23170000, 10))
    alumnos.eliminar(23170000)

    alumnos.guardar_como_json()

    alumnosDesdeJson = instanciar_alumnos("Alumno.json")

    a3 = Alumno("Alumno nuevo", "nuevo", 20, 2317, 5)
    alumnosDesdeJson.agregar(a3)

    alumnosDesdeJson.mostrar_diccionario()




