import json
from arreglo import Arreglo

class Alumno(Arreglo):
    def __init__(self, nombre=None, apellido=None, edad=None, matricula=None, promedio=None, **kwargs):
        if nombre is None and apellido is None and edad is None and matricula is None and promedio is None:
            # Arreglo de alumnos (como colección)
            Arreglo.__init__(self)
            self.es_arreglo = True
        else:
            # Instancia individual de alumno
            self.id = matricula
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.matricula = matricula
            self.promedio = promedio
            self.es_arreglo = False

    def leerJson(self, archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            data=json.load(f)
            return self.instanciar(data)

    def es_alumno(self,dic):
        campos_obligatorios = {"nombre", "apellido", "edad", "matricula", "promedio"}
        return campos_obligatorios.issubset(dic.keys())

    def instanciar(self, entrada):
        if isinstance(entrada, str):
            datos = self.leerJson(entrada)
        else:
            datos = entrada

        if isinstance(datos, list):
            for d in datos:
                if self.es_alumno(d):
                    alumno = Alumno(**d)
                    self.agregar(alumno)
                else:
                    print(
                        "ERROR: El archivo contiene datos que no corresponden a alumnos. Usa un JSON de alumnos válido.")
                    return False
        elif isinstance(datos, dict):
            if self.es_alumno(datos):
                alumno = Alumno(**datos)
                self.agregar(alumno)
            else:
                print("ERROR: El archivo no corresponde a un alumno válido. Usa un JSON de alumnos válido.")
                return False

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


# Ejemplo de uso (para pruebas):
if __name__ == "__main__":
    # Crear y guardar alumnos
    a1 = Alumno("Alberto", "Trejo", 18, 23170093, 10)
    a2 = Alumno("Jesus", "De la rosa", 19, 23170119, 9.3)

    alumnos = Alumno()
    alumnos.agregar(a1)
    alumnos.agregar(a2)
    alumnos.agregar(Alumno("Saul", "Sanchez", 20, 23170000, 10))
    alumnos.eliminar(23170000)

    alumnos.guardar_como_json()
    alumnos.mostrar_diccionario()

    # Instanciar desde archivo
    alumnosDesdeJson = Alumno()
    alumnosDesdeJson.instanciar("Alumno.json")


