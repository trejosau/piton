import streamlit as st
import os
from alumno import Alumno


class AppAlumnos:
    def __init__(self, colecciones):
        self.colecciones = colecciones
        self.cargar_alumnos_inicial()

    def cargar_alumnos_inicial(self):
        if "Alumnos desde archivo" not in self.colecciones:
            alumnos_desde_json = Alumno()
            if alumnos_desde_json.cargar_desde_db():
                self.colecciones["Alumnos desde archivo"] = alumnos_desde_json
                st.info("Colección 'Alumnos desde archivo' cargada desde base de datos")
            elif os.path.exists("Alumno.json"):
                alumnos_desde_json.leerJson("Alumno.json")
                self.colecciones["Alumnos desde archivo"] = alumnos_desde_json
                st.info("Colección 'Alumnos desde archivo' cargada desde archivo JSON")

    def formulario_alumno(self):
        nombre = st.text_input("Nombre", key="form_nombre")
        apellido = st.text_input("Apellido", key="form_apellido")
        edad = st.number_input("Edad", min_value=0, max_value=120, value=18, key="form_edad")
        matricula = st.number_input("Matrícula", min_value=23170, key="form_matricula")
        promedio = st.number_input("Promedio", min_value=0.0, max_value=10.0, value=8.0, step=0.1, key="form_promedio")
        return Alumno(nombre, apellido, edad, matricula, promedio)

    def crear_coleccion_vacia(self):
        st.subheader("Crear nueva colección de alumnos")
        with st.form("form_nueva_coleccion_alumnos"):
            nombre = st.text_input("Nombre para la colección")
            crear = st.form_submit_button("Crear colección")
            if crear:
                if nombre and nombre not in self.colecciones:
                    self.colecciones[nombre] = Alumno()
                    st.success(f"Colección '{nombre}' creada.")
                    st.rerun()
                else:
                    st.warning("Ya existe")

    def mostrar_tarjetas_colecciones(self):
        st.subheader("Colecciones de alumnos existentes")
        if not self.colecciones:
            st.info("No hay colecciones registradas.")
            return

        cols = st.columns(min(4, len(self.colecciones)))
        for i, (nombre, coleccion) in enumerate(self.colecciones.items()):
            with cols[i % len(cols)]:
                st.markdown(
                    f"""
                    <div style='
                        display:flex;flex-direction:column;align-items:center;
                        justify-content:center;width:256px;height:128px;
                        background:#262730;color:#fff;border:2.5px solid #585858;
                        border-radius:20px;text-align:center;'>
                        <div style="font-size:1.15em;font-weight:600;">{nombre}</div>
                        <div style="font-size:.93em;opacity:0.8;">Alumnos: <b>{len(coleccion.items)}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar alumnos", key=f"mostrar_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    def tabla_crud_alumnos(self, coleccion):
        st.subheader("Alumnos registrados")
        alumnos = coleccion.items
        if not alumnos:
            st.info("No hay alumnos en esta colección.")
            return

        for idx, al in enumerate(alumnos):
            with st.expander(f"{al.nombre} {al.apellido} (Matrícula: {al.matricula})", expanded=True):
                nuevo_nombre = st.text_input("Nombre", al.nombre, key=f"edit_nombre_{al.matricula}")
                nuevo_apellido = st.text_input("Apellido", al.apellido, key=f"edit_apellido_{al.matricula}")
                nueva_edad = st.number_input("Edad", 0, 120, al.edad, key=f"edit_edad_{al.matricula}")
                nueva_matricula = st.number_input("Matrícula", min_value=23170, value=al.matricula,
                                                  key=f"edit_matricula_{al.matricula}")
                nuevo_promedio = st.number_input("Promedio", 0.0, 10.0, al.promedio, step=0.1,
                                                 key=f"edit_prom_{al.matricula}")

                col1, col2 = st.columns(2)
                if col1.button("Guardar", key=f"save_{al.matricula}"):
                    matriculas_existentes = [a.matricula for i, a in enumerate(alumnos) if i != idx]
                    if nueva_matricula in matriculas_existentes:
                        st.error("La matrícula ya existe.")
                    else:
                        al.nombre = nuevo_nombre
                        al.apellido = nuevo_apellido
                        al.edad = nueva_edad
                        al.matricula = nueva_matricula
                        al.promedio = nuevo_promedio
                        st.success("Alumno actualizado.")
                        st.rerun()

                if col2.button("Eliminar", key=f"del_{al.matricula}"):
                    coleccion.eliminar(al.matricula)
                    st.warning("Alumno eliminado.")
                    st.rerun()

    def agregar_alumno_nuevo(self, coleccion):
        st.subheader("Agregar nuevo alumno")
        with st.form("form_agregar_alumno"):
            nuevo_alumno = self.formulario_alumno()
            agregar = st.form_submit_button("Agregar alumno")
            if agregar:
                matriculas_existentes = [al.matricula for al in coleccion.items]
                if nuevo_alumno.matricula in matriculas_existentes:
                    st.error("La matrícula ya existe en esta colección.")
                else:
                    coleccion.agregar(nuevo_alumno)
                    st.success("Alumno agregado correctamente.")
                    st.rerun()

    def opciones_extra_alumno(self, coleccion, coleccion_actual):
        if st.button("Guardar colección", key=f"guardar_{coleccion_actual}"):
            try:
                coleccion.guardar_como_json()
                st.success(f"Colección '{coleccion_actual}' guardada correctamente.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

        if st.button("Mostrar como diccionario", key=f"dict_{coleccion_actual}_alumno"):
            st.json(coleccion.convADiccionario())

        if st.button("Ocultar alumnos"):
            st.session_state["coleccion_mostrando"] = None

    def render(self):
        self.crear_coleccion_vacia()
        st.markdown("---")
        self.mostrar_tarjetas_colecciones()

        coleccion_actual = st.session_state.get("coleccion_mostrando")
        if coleccion_actual:
            st.markdown("---")
            st.subheader(f"Colección activa: {coleccion_actual}")
            coleccion = self.colecciones[coleccion_actual]
            self.tabla_crud_alumnos(coleccion)
            self.agregar_alumno_nuevo(coleccion)
            self.opciones_extra_alumno(coleccion, coleccion_actual)