import streamlit as st
import alumno_app
import grupo_app
import maestro_app

st.set_page_config(page_title="Gestor de Colecciones Escolares", layout="wide")
st.title("Gestor de Colecciones Escolares")

# ---- Selección de tipo de colección ----
tipo = st.sidebar.selectbox("Selecciona un tipo de colección", ["Alumnos", "Maestros", "Grupos"])

if "tipo_anterior" not in st.session_state:
    st.session_state["tipo_anterior"] = tipo
elif st.session_state["tipo_anterior"] != tipo:
    st.session_state["coleccion_mostrando"] = None
    st.session_state["tipo_anterior"] = tipo

# Asignar colecciones según tipo
colecciones_key = f"colecciones_{tipo.lower()}"
if colecciones_key not in st.session_state:
    st.session_state[colecciones_key] = {}

# Renderizado condicional por tipo
if tipo == "Alumnos":
    alumno_app.render(st.session_state[colecciones_key])

if tipo == "Maestros":
    maestro_app.render(st.session_state[colecciones_key])

if tipo == "Grupos":
    grupo_app.render(st.session_state[colecciones_key])