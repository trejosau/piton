import streamlit as st
import pandas as pd
from maestro import Maestro
import os

class AppMaestros:
    def __init__(self, colecciones):
        self.colecciones = colecciones
        self.cargar_maestros_inicial()

    def cargar_maestros_inicial(self):
        if "Maestros inicial" not in self.colecciones:
            maestros_inicial = Maestro()
            if maestros_inicial.cargar_desde_db():
                self.colecciones["Maestros inicial"] = maestros_inicial
                st.info("Colección 'Maestros inicial' cargada desde base de datos")
            elif os.path.exists("Maestro.json"):
                maestros_inicial.leerJson("Maestro.json")
                self.colecciones["Maestros inicial"] = maestros_inicial
                st.info("Colección 'Maestros inicial' cargada desde archivo JSON")

    def formulario_maestro(self, key_prefix=""):
        nombre = st.text_input("Nombre", key=f"{key_prefix}_nombre")
        apellido = st.text_input("Apellido", key=f"{key_prefix}_apellido")
        edad = st.number_input("Edad", min_value=18, max_value=120, value=18, key=f"{key_prefix}_edad")
        num_maestro = st.text_input("ID del maestro", key=f"{key_prefix}_num_maestro")
        especialidad = st.text_input("Especialidad", key=f"{key_prefix}_especialidad")
        return Maestro(nombre, apellido, edad, num_maestro, especialidad)

    def crear_coleccion_vacia_maestro(self):
        st.subheader("Crear nueva colección de maestros")
        with st.form("form_nueva_coleccion_maestros"):
            nombre = st.text_input("Nombre para la colección")
            crear = st.form_submit_button("Crear colección")
            if crear:
                if nombre and nombre not in self.colecciones:
                    self.colecciones[nombre] = Maestro()
                    st.success(f"Colección '{nombre}' creada.")
                    st.rerun()
                else:
                    st.warning("Nombre inválido o ya existe una colección con ese nombre.")

    def mostrar_tarjetas_colecciones_maestros(self):
        st.subheader("Colecciones de maestros existentes")
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
                        background:#23233b;color:#fff;border:2.5px solid #5a5a5a;
                        border-radius:20px;text-align:center;'>
                        <div style="font-size:1.15em;font-weight:600;">{nombre}</div>
                        <div style="font-size:.93em;opacity:0.8;">Maestros: <b>{len(coleccion.items)}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar maestros", key=f"mostrar_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    def tabla_crud_maestros(self, coleccion):
        st.subheader("Maestros registrados")
        maestros = coleccion.items
        if maestros:
            df = pd.DataFrame([m.convADiccionario() for m in maestros])
            st.dataframe(df, hide_index=True)
            st.markdown("### Editar o eliminar maestros")
            for idx, m in enumerate(maestros):
                cols = st.columns([2, 2, 1, 2, 2, 1, 1])
                nuevo_nombre = cols[0].text_input("Nombre", m.nombre, key=f"edit_nombre_{m.num_maestro}")
                nuevo_apellido = cols[1].text_input("Apellido", m.apellido, key=f"edit_apellido_{m.num_maestro}")
                nueva_edad = cols[2].number_input("Edad", 18, 120, m.edad, key=f"edit_edad_{m.num_maestro}")
                nuevo_id = cols[3].text_input("ID", m.num_maestro, key=f"edit_id_{m.num_maestro}")
                nueva_especialidad = cols[4].text_input("Especialidad", m.especialidad, key=f"edit_esp_{m.num_maestro}")

                if cols[5].button("Guardar", key=f"save_{m.num_maestro}"):
                    ids_existentes = [ma.num_maestro for i, ma in enumerate(maestros) if i != idx]
                    if nuevo_id in ids_existentes:
                        st.error("El ID ya existe.")
                    else:
                        m.nombre = nuevo_nombre
                        m.apellido = nuevo_apellido
                        m.edad = nueva_edad
                        m.num_maestro = nuevo_id
                        m.especialidad = nueva_especialidad
                        st.success("Maestro actualizado.")
                        st.rerun()

                if cols[6].button("Eliminar", key=f"del_{m.num_maestro}"):
                    coleccion.eliminar(m.num_maestro)
                    st.warning("Maestro eliminado.")
                    st.rerun()
        else:
            st.info("No hay maestros en esta colección.")

    def agregar_maestro_nuevo(self, coleccion, coleccion_actual):
        st.subheader("Agregar nuevo maestro")
        with st.form(f"form_agregar_maestro_{coleccion_actual}"):
            nuevo_maestro = self.formulario_maestro(key_prefix=f"nuevo_{coleccion_actual}")
            agregar = st.form_submit_button("Agregar maestro")
            if agregar:
                ids_existentes = [m.num_maestro for m in coleccion.items]
                if nuevo_maestro.num_maestro in ids_existentes:
                    st.error("El ID ya existe en esta colección.")
                else:
                    coleccion.agregar(nuevo_maestro)
                    st.success("Maestro agregado correctamente.")
                    st.rerun()

    def opciones_extra_maestro(self, coleccion, coleccion_actual):
        if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}_maestro"):
            coleccion.guardar_como_json()
            st.success(f"Colección '{coleccion_actual}' guardada.")

        if st.button("Mostrar como diccionario", key=f"dict_{coleccion_actual}_maestro"):
            st.json(coleccion.convADiccionario())

        if st.button("Ocultar maestros"):
            st.session_state["coleccion_mostrando"] = None

    def render(self):
        self.crear_coleccion_vacia_maestro()
        st.markdown("---")
        self.mostrar_tarjetas_colecciones_maestros()

        coleccion_actual = st.session_state.get("coleccion_mostrando")
        if coleccion_actual:
            st.markdown("---")
            st.subheader(f"Colección activa: {coleccion_actual}")
            coleccion = self.colecciones[coleccion_actual]
            self.tabla_crud_maestros(coleccion)
            self.agregar_maestro_nuevo(coleccion, coleccion_actual)
            self.opciones_extra_maestro(coleccion, coleccion_actual)