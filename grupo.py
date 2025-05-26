import json

from alumno import Alumno, instanciar_alumnos
from arreglo import Arreglo
from maestro import Maestro, instanciar_maestros


def leerJson(archivo):
    import json
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def instanciar_grupo_json(archivo):

    datos = leerJson(archivo)

    def crear_grupo(d):
        maestro = None
        if d.get("maestro"):
            maestro = instanciar_maestros(d["maestro"])

        grupo = Grupo(
            nombre=d.get("nombre"),
            maestro=maestro
        )
        alumnos_datos = d.get("alumnos", [])
        alumnos_inst = instanciar_alumnos(alumnos_datos)
        if alumnos_inst:
            if getattr(alumnos_inst, "es_arreglo", False):
                grupo.alumnos.items.extend(alumnos_inst.items)
            else:
                grupo.alumnos.agregar(alumnos_inst)
        if "id" in d:
            grupo.id = d["id"]
        return grupo

    if isinstance(datos, list):
        arreglo_grupos = Grupo()
        for d in datos:
            arreglo_grupos.agregar(crear_grupo(d))
        return arreglo_grupos
    elif isinstance(datos, dict):
        return crear_grupo(datos)
    else:
        print("Formato de JSON no reconocido")
        return None


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

    def convADiccionario(self):
        if self.es_arreglo:
            return self.convADiccionarios()

        return {
            "id": self.id,
            "nombre": self.nombre,
            "maestro": self.maestro.convADiccionario() if self.maestro else None,
            "alumnos": [alumno.convADiccionario() for alumno in self.alumnos.items]
        }

    def getDict(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

    def guardar_como_json(self):
        clase = self.__class__.__name__
        nombre_archivo = f"{clase}.json"

        datos = self.convADiccionario()

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

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
    grupo_mobile = Grupo("Desarrollo Móvil", m1)
    grupo_mobile2 = Grupo("Desarrollo Móvil2", m1)

    grupo_mobile.alumnos.agregar(a1, a2)
    grupo_mobile.asignar_maestro(m1)

    grupo_mobile.alumnos.actualizar(a1, 'promedio', 5)

    grupo_mobile2.alumnos.agregar(a1,a2)
    grupo_mobile2.asignar_maestro(m1)

    grupos_mobile = Grupo()
    grupos_mobile.agregar(grupo_mobile, grupo_mobile2)

    grupos_mobile.guardar_como_json()

    grupos_desdeJson = instanciar_grupo_json("Grupo.json")
    grupos_desdeJson.mostrar_diccionario()



