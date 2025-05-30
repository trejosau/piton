import streamlit as st
import json
import pandas as pd
from alumno import Alumno  # Usa exactamente tu clase Alumno

st.set_page_config(page_title="Colecciones Escolares", layout="wide")
st.title("Colecciones de Alumnos")

# ---- Estado global ----
if "colecciones_alumnos" not in st.session_state:
    st.session_state["colecciones_alumnos"] = {}
if "coleccion_mostrando" not in st.session_state:
    st.session_state["coleccion_mostrando"] = None

colecciones = st.session_state["colecciones_alumnos"]

# ---- Apartado para cargar colección desde JSON ----
st.subheader("Cargar colección de alumnos desde archivo JSON")
with st.form("form_json_alumnos"):
    archivo = st.file_uploader("Selecciona un archivo JSON válido de alumnos", type=["json"])
    nombre_col = st.text_input("Nombre para la nueva colección")
    cargar = st.form_submit_button("Cargar colección")
    if cargar:
        if archivo and nombre_col and nombre_col not in colecciones:
            try:
                data = json.load(archivo)
                alumnos_cargados = Alumno()
                resultado = alumnos_cargados.instanciar(data)
                if resultado is False or len(alumnos_cargados) == 0:
                    st.error("El archivo no corresponde a una colección válida de alumnos. Usa un JSON de alumnos válido.")
                else:
                    colecciones[nombre_col] = alumnos_cargados
                    st.success(f"Colección '{nombre_col}' cargada con {len(alumnos_cargados)} alumnos.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error cargando JSON: {e}")
        else:
            st.warning("Falta archivo, nombre, o el nombre ya existe.")
st.markdown("---")

# ---- Agregar colección manualmente ----
with st.form("agregar_coleccion"):
    nombre = st.text_input("Nombre de la nueva colección")
    sub = st.form_submit_button("Agregar colección")
    if sub:
        if nombre and nombre not in colecciones:
            colecciones[nombre] = Alumno()  # Colección vacía
            st.success(f"Colección '{nombre}' creada.")
            st.rerun()
        else:
            st.warning("Nombre inválido o colección existente.")

st.markdown("---")
st.subheader("Colecciones de Alumnos")

# ---- Tarjetas cuadradas de colecciones ----
if not colecciones:
    st.info("No hay colecciones registradas.")
else:
    cols = st.columns(min(4, len(colecciones)))
    for i, (nombre, coleccion) in enumerate(colecciones.items()):
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
                    background: #262730;
                    color: #fff;
                    border: 2.5px solid #585858;
                    border-radius: 20px;
                    text-align: center;
                '>
                    <div style="font-size:1.15em; font-weight:600; margin-bottom:2px;">Coleccion: {nombre}</div>
                    <div style="font-size:.93em; opacity:0.8;">Alumnos: <span style="font-weight:700;">{coleccion}</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Mostrar alumnos", key=f"mostrar_{nombre}"):
                st.session_state["coleccion_mostrando"] = nombre

# ---- Mostrar tabla y agregar alumnos ----
coleccion_actual = st.session_state.get("coleccion_mostrando")
if coleccion_actual:
    st.subheader(f"Alumnos de la colección: {coleccion_actual}")
    coleccion = colecciones[coleccion_actual]
    alumnos = coleccion.items

    # Tabla
    if alumnos:
        df = pd.DataFrame([{
            "Nombre": al.nombre,
            "Apellido": al.apellido,
            "Edad": al.edad,
            "Matrícula": al.matricula,
            "Promedio": al.promedio
        } for al in alumnos])
        st.dataframe(df, hide_index=True)

        # --- Acciones CRUD por alumno ---
        st.markdown("### Editar o eliminar alumnos")
        for idx, al in enumerate(alumnos):
            cols = st.columns([2, 2, 1, 2, 2, 1, 1])
            with cols[0]:
                nuevo_nombre = st.text_input(f"Nombre_{al.matricula}", al.nombre, key=f"edit_nombre_{al.matricula}")
            with cols[1]:
                nuevo_apellido = st.text_input(f"Apellido_{al.matricula}", al.apellido, key=f"edit_apellido_{al.matricula}")
            with cols[2]:
                nueva_edad = st.number_input(f"Edad_{al.matricula}", min_value=0, max_value=120, value=al.edad, key=f"edit_edad_{al.matricula}")
            with cols[3]:
                nueva_matricula = st.number_input(f"Matrícula_{al.matricula}", min_value=23170, value=al.matricula, key=f"edit_matricula_{al.matricula}")
            with cols[4]:
                nuevo_promedio = st.number_input(f"Promedio_{al.matricula}", min_value=0.0, max_value=10.0, step=0.1,  value=float(al.promedio), key=f"edit_prom_{al.matricula}")
            with cols[5]:
                if st.button("Guardar", key=f"save_{al.matricula}"):
                    # Validar matrícula única
                    matriculas_existentes = [a.matricula for i, a in enumerate(alumnos) if i != idx]
                    if nueva_matricula in matriculas_existentes:
                        st.error("La matrícula ya existe en esta colección.")
                    else:
                        al.nombre = nuevo_nombre
                        al.apellido = nuevo_apellido
                        al.edad = nueva_edad
                        al.matricula = nueva_matricula
                        al.promedio = nuevo_promedio
                        st.success("Alumno actualizado.")
                        st.rerun()
            with cols[6]:
                if st.button("Eliminar", key=f"del_{al.matricula}"):
                    coleccion.eliminar(al.matricula)
                    st.warning("Alumno eliminado.")
                    st.rerun()

    else:
        st.info("No hay alumnos en esta colección.")

    # Agregar alumno
    with st.form(f"agregar_alumno_{coleccion_actual}"):
        n = st.text_input("Nombre")
        a = st.text_input("Apellido")
        e = st.number_input("Edad", min_value=0, max_value=120, value=18)
        m = st.number_input("Matrícula", min_value=23170)
        p = st.number_input("Promedio", min_value=0.0, max_value=10.0, step=0.1, value=8.0)
        sub_al = st.form_submit_button("Agregar alumno")
        if sub_al:
            if n and a and m:
                matriculas_existentes = [al.matricula for al in alumnos]
                if m in matriculas_existentes:
                    st.error("La matrícula ya existe en esta colección. Debe ser única.")
                else:
                    coleccion.agregar(Alumno(n, a, e, m, p))
                    st.success("Alumno agregado.")
                    st.rerun()
            else:
                st.warning("Llena todos los campos obligatorios.")

    # Ocultar colección actual
    if st.button("Ocultar alumnos", key="ocultar_alumnos"):
        st.session_state["coleccion_mostrando"] = None

    # Guardar como JSON
    if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}"):
        obj = colecciones[coleccion_actual]
        obj.guardar_como_json()
        st.success(f"¡Colección '{coleccion_actual}' guardada como JSON!")

    # Mostrar como diccionario JSON visual
    if st.button("Mostrar en diccionario", key=f"mostrar_dict_{coleccion_actual}"):
        obj = colecciones[coleccion_actual]
        st.json(obj.convADiccionario())
