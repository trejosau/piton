import os
from grupo import Grupo
import streamlit as st
import json
import pandas as pd


class AppGrupos:
    def __init__(self, colecciones, maestros_disponibles=None, alumnos_disponibles=None):
        self.colecciones = colecciones
        self.maestros_disponibles = maestros_disponibles or []
        self.alumnos_disponibles = alumnos_disponibles or []
        self.cargar_grupos_inicial()
        self.cargar_datos_relacionados()  # Nueva función para cargar datos relacionados

    def cargar_grupos_inicial(self):
        if "Grupos desde archivo" not in self.colecciones:
            grupos_desde_json = Grupo()
            if grupos_desde_json.cargar_desde_db():
                self.colecciones["Grupos desde archivo"] = grupos_desde_json
                st.info("Colección 'Grupos desde archivo' cargada desde base de datos")
            elif os.path.exists("Grupo.json"):
                grupos_desde_json.leerJson("Grupo.json")
                self.colecciones["Grupos desde archivo"] = grupos_desde_json
                st.info("Colección 'Grupos desde archivo' cargada desde archivo JSON")

    def cargar_datos_relacionados(self):
        if not self.maestros_disponibles and "colecciones_maestros" in st.session_state:
            maestros = []
            for col in st.session_state["colecciones_maestros"].values():
                maestros.extend(col.items)
            self.maestros_disponibles = maestros

        if "colecciones_alumnos" not in st.session_state:
            st.session_state["colecciones_alumnos"] = {}

        if "Alumnos desde archivo" not in st.session_state["colecciones_alumnos"]:
            from alumno import Alumno
            alumnos_desde_archivo = Alumno()
            if alumnos_desde_archivo.cargar_desde_db():
                st.session_state["colecciones_alumnos"]["Alumnos desde archivo"] = alumnos_desde_archivo
            elif os.path.exists("Alumno.json"):
                try:
                    alumnos_desde_archivo.leerJson("Alumno.json")
                    st.session_state["colecciones_alumnos"]["Alumnos desde archivo"] = alumnos_desde_archivo
                except Exception as e:
                    print(f"Error al cargar alumnos desde archivo: {e}")

    def crear_coleccion_y_grupo(self):
        st.subheader("Crear nueva colección y grupo")
        with st.form("form_nueva_coleccion_grupo"):
            nombre_coleccion = st.text_input("Nombre de la nueva colección")
            nombre_grupo = st.text_input("Nombre del grupo")
            maestro_seleccionado = None
            if self.maestros_disponibles:
                maestro_seleccionado = st.selectbox(
                    "Selecciona un maestro",
                    self.maestros_disponibles,
                    format_func=lambda m: f"{m.nombre} {m.apellido} (ID: {m.num_maestro})"
                )
            else:
                st.warning("Primero registra maestros en el módulo correspondiente.")
            submit = st.form_submit_button("Crear colección y agregar grupo")
            if submit:
                if nombre_coleccion and nombre_grupo and maestro_seleccionado:
                    grupo = Grupo(nombre_grupo, maestro_seleccionado)
                    nueva_coleccion = Grupo()
                    nueva_coleccion.agregar(grupo)
                    if nombre_coleccion not in self.colecciones:
                        self.colecciones[nombre_coleccion] = nueva_coleccion
                        st.success(f"Colección '{nombre_coleccion}' creada con grupo '{nombre_grupo}'.")
                        st.rerun()
                    else:
                        st.warning("Ya existe una colección con ese nombre.")
                else:
                    st.warning("Completa todos los campos obligatorios.")

    def mostrar_tarjetas_colecciones_grupos(self):
        st.subheader("Colecciones de Grupos")
        if not self.colecciones:
            st.info("No hay colecciones registradas.")
            return
        cols = st.columns(min(4, max(1, len(self.colecciones))))
        for i, (nombre, coleccion) in enumerate(self.colecciones.items()):
            with cols[i % len(cols)]:
                st.markdown(
                    f"""
                    <div style='
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        width: 512px;
                        height: 128px;
                        background: #1c1c1e;
                        color: #fff;
                        border: 2.5px solid #5a5a5a;
                        border-radius: 20px;
                        text-align: center;
                    '>
                        <div style="font-size:1.15em; font-weight:600;">Colección: {nombre}</div>
                        <div style="font-size:.93em; opacity:0.8;">Grupos: <b>{len(coleccion.items)}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar grupos", key=f"mostrar_grupo_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    def obtener_alumnos_disponibles(self, alumnos_grupo):
        """Obtener lista de alumnos disponibles para agregar al grupo"""
        alumnos_disponibles = []
        matriculas_en_grupo = [al.matricula for al in alumnos_grupo]

        # Buscar en todas las colecciones de alumnos
        for coleccion_al in st.session_state.get("colecciones_alumnos", {}).values():
            for alumno in coleccion_al.items:
                if alumno.matricula not in matriculas_en_grupo:
                    # Evitar duplicados por matrícula
                    if not any(a.matricula == alumno.matricula for a in alumnos_disponibles):
                        alumnos_disponibles.append(alumno)

        return alumnos_disponibles

    def detalle_coleccion_actual(self):
        coleccion_actual = st.session_state.get("coleccion_mostrando")
        if coleccion_actual and coleccion_actual in self.colecciones:
            st.subheader(f"Grupos de la colección: {coleccion_actual}")
            coleccion = self.colecciones[coleccion_actual]
            grupos = getattr(coleccion, "items", [])
            if grupos:
                for g in grupos:
                    st.markdown(f"### Grupo: {g.nombre}")
                    maestro = g.maestro
                    st.markdown(
                        f"**Maestro:** {maestro.nombre} {maestro.apellido}, ID: {maestro.num_maestro}, Especialidad: {maestro.especialidad}"
                        if maestro else "Sin maestro asignado."
                    )

                    alumnos = getattr(g.alumnos, "items", [])
                    if alumnos:
                        df = pd.DataFrame([{
                            "Nombre": a.nombre,
                            "Apellido": a.apellido,
                            "Edad": a.edad,
                            "Matrícula": a.matricula,
                            "Promedio": a.promedio
                        } for a in alumnos])
                        st.dataframe(df, hide_index=True)
                    else:
                        st.info(f"No hay alumnos en el grupo '{g.nombre}'")

                    # Obtener alumnos disponibles para agregar
                    alumnos_disponibles = self.obtener_alumnos_disponibles(alumnos)

                    if alumnos_disponibles:
                        alumno_sel = st.selectbox(
                            f"Selecciona alumno para agregar al grupo '{g.nombre}'",
                            alumnos_disponibles,
                            format_func=lambda a: f"{a.nombre} {a.apellido} ({a.matricula})",
                            key=f"sel_alumno_{g.id}"
                        )
                        if st.button("Agregar alumno al grupo", key=f"agregar_{g.id}"):
                            g.alumnos.agregar(alumno_sel)
                            st.success(f"Alumno {alumno_sel.nombre} {alumno_sel.apellido} agregado al grupo.")
                            st.rerun()
                    else:
                        st.info("No hay alumnos disponibles para agregar a este grupo.")

                    st.markdown("---")  # Separador entre grupos
            else:
                st.info("No hay grupos en esta colección.")

            if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}_grupo"):
                coleccion.guardar_como_json()
                st.success(f"Colección '{coleccion_actual}' guardada como JSON.")

            if st.button("Mostrar colección como diccionario", key=f"mostrar_dict_{coleccion_actual}_grupo"):
                st.subheader(f"Diccionario JSON de la colección '{coleccion_actual}'")
                diccionario = coleccion.convADiccionario()
                st.json(diccionario)

            if st.button("Ocultar grupos"):
                st.session_state["coleccion_mostrando"] = None

    def render(self):
        st.header("Colecciones de Grupos")

        self.cargar_datos_relacionados()

        self.crear_coleccion_y_grupo()
        st.markdown("---")
        self.mostrar_tarjetas_colecciones_grupos()
        self.detalle_coleccion_actual()