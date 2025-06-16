import json
from arreglo import Arreglo
from alumno import Alumno
from maestro import Maestro
from db_manager import DBManager


class Grupo(Arreglo):
    _id_counter = 1

    def __init__(self, nombre=None, maestro=None, **kwargs):
        if nombre is None and maestro is None:
            super().__init__()
            self.es_arreglo = True
        else:
            self.id = Grupo._id_counter
            Grupo._id_counter += 1
            self.nombre = nombre
            self.maestro = maestro
            self.alumnos = Alumno()
            self.es_arreglo = False

    def leerJson(self, archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    def asignar_maestro(self, maestro):
        self.maestro = maestro

    def instanciar(self, entrada):
        if isinstance(entrada, str):
            datos = self.leerJson(entrada)
        else:
            datos = entrada

        self.items.clear()
        if isinstance(datos, list):
            for d in datos:
                grupo = Grupo()
                grupo.instanciar(d)
                self.agregar(grupo)
        elif isinstance(datos, dict):
            self.id = datos.get("id", Grupo._id_counter)
            Grupo._id_counter = max(Grupo._id_counter, self.id + 1)
            self.nombre = datos.get("nombre")

            if "maestro" in datos and datos["maestro"]:
                self.maestro = Maestro(**datos["maestro"])
            else:
                self.maestro = None

            if "alumnos" in datos:
                self.alumnos = Alumno()
                self.alumnos.instanciar(datos["alumnos"])
            else:
                self.alumnos = Alumno()
            self.es_arreglo = False

    def cargar_desde_db(self):
        db = DBManager()
        if db.intentar_conexion():
            datos = db.cargar_datos("grupos", "Grupo")
            if datos:
                self.instanciar(datos)
                return True
        try:
            datos = self.leerJson("Grupo.json")
            self.instanciar(datos)
            return True
        except:
            return False

    def convADiccionario(self):
        if self.es_arreglo:
            return self.convADiccionarios()
        return {
            "id": self.id,
            "nombre": self.nombre,
            "maestro": self.maestro.convADiccionario() if self.maestro else None,
            "alumnos": [alumno.convADiccionario() for alumno in self.alumnos.items]
        }

    def guardar_como_json(self):
        clase = self.__class__.__name__
        datos = self.convADiccionario()

        db = DBManager()

        db.guardar_datos("grupos", datos, clase)

    def __str__(self):
        if self.es_arreglo:
            return super().__str__()
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
    grupo_mobile2.alumnos.agregar(a1, a2)
    grupo_mobile2.asignar_maestro(m1)

    grupos_mobile = Grupo()
    grupos_mobile.agregar(grupo_mobile, grupo_mobile2)

    grupos_mobile.guardar_como_json()

    grupos_desdeJson = Grupo()
    grupos_desdeJson.cargar_desde_db()
    grupos_desdeJson.guardar_como_json()