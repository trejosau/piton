import streamlit as st
from alumno_app import AppAlumnos
from grupo_app import AppGrupos
from maestro_app import AppMaestros
from db_manager import DBManager


class ColeccionesApp:
    def __init__(self):
        st.set_page_config(page_title="Gestor de Colecciones Escolares", layout="wide")
        st.title("Gestor de Colecciones Escolares")

        self.inicializar_db()

        self.tipo = st.sidebar.selectbox(
            "Selecciona un tipo de colección",
            ["Alumnos", "Maestros", "Grupos"]
        )

        if "tipo_anterior" not in st.session_state:
            st.session_state["tipo_anterior"] = self.tipo
        elif st.session_state["tipo_anterior"] != self.tipo:
            st.session_state["coleccion_mostrando"] = None
            st.session_state["tipo_anterior"] = self.tipo

        self.colecciones_key = f"colecciones_{self.tipo.lower()}"
        if self.colecciones_key not in st.session_state:
            st.session_state[self.colecciones_key] = {}

    def inicializar_db(self):
        db = DBManager()
        with st.sidebar:
            st.markdown("### Estado de la Base de Datos")
            db.mostrar_estado_conexion()

    def render(self):
        if self.tipo == "Alumnos":
            app_alumnos = AppAlumnos(st.session_state[self.colecciones_key])
            app_alumnos.render()

        if self.tipo == "Maestros":
            app_maestros = AppMaestros(st.session_state[self.colecciones_key])
            app_maestros.render()

        if self.tipo == "Grupos":
            app_grupos = AppGrupos(st.session_state[self.colecciones_key])
            app_grupos.render()


if __name__ == "__main__":
    app = ColeccionesApp()
    app.render()