import streamlit as st
import json
import pandas as pd
from grupo import Grupo
from alumno import Alumno
from maestro import Maestro

def render(colecciones):
    st.header("Colecciones de Grupos")

    # ---- Cargar colección desde archivo JSON ----
    st.subheader("Cargar colección de grupos desde archivo JSON")
    with st.form("form_json_grupos"):
        archivo = st.file_uploader("Selecciona un archivo JSON válido de grupos", type=["json"])
        nombre_col = st.text_input("Nombre para la nueva colección de grupos")
        cargar = st.form_submit_button("Cargar colección")
        if cargar:
            if archivo and nombre_col and nombre_col not in colecciones:
                try:
                    data = json.load(archivo)
                    grupos_cargados = Grupo()
                    grupos_cargados.instanciar(data)
                    items_ok = hasattr(grupos_cargados, "items") and isinstance(grupos_cargados.items, list) and grupos_cargados.items
                    if not items_ok:
                        st.error("El archivo no contiene grupos válidos.")
                    else:
                        colecciones[nombre_col] = grupos_cargados
                        st.success(f"Colección '{nombre_col}' cargada con {len(grupos_cargados.items)} grupos.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error cargando JSON: {e}")
            else:
                st.warning("Falta archivo, nombre o ya existe una colección con ese nombre.")
    st.markdown("---")

    # ---- Crear nueva colección y grupo ----
    with st.form("form_nueva_coleccion_grupo"):
        nombre_coleccion = st.text_input("Nombre de la nueva colección")
        nombre_grupo = st.text_input("Nombre del grupo")

        maestros_disponibles = []
        if "colecciones_maestros" in st.session_state:
            for col in st.session_state["colecciones_maestros"].values():
                maestros_disponibles.extend(col.items)

        if maestros_disponibles:
            maestro_seleccionado = st.selectbox(
                "Selecciona un maestro",
                maestros_disponibles,
                format_func=lambda m: f"{m.nombre} {m.apellido} (ID: {m.num_maestro})"
            )
        else:
            st.warning("Primero registra maestros en el módulo correspondiente.")
            maestro_seleccionado = None

        submit = st.form_submit_button("Crear colección y agregar grupo")

        if submit:
            if nombre_coleccion and nombre_grupo and maestro_seleccionado:
                grupo = Grupo(nombre_grupo, maestro_seleccionado)
                nueva_coleccion = Grupo()
                nueva_coleccion.agregar(grupo)

                if nombre_coleccion not in colecciones:
                    colecciones[nombre_coleccion] = nueva_coleccion
                    st.success(f"Colección '{nombre_coleccion}' creada con grupo '{nombre_grupo}'.")
                    st.rerun()
                else:
                    st.warning("Ya existe una colección con ese nombre.")
            else:
                st.warning("Completa todos los campos obligatorios.")
    st.markdown("---")

    # ---- Mostrar colecciones ----
    st.subheader("Colecciones de Grupos")

    if not colecciones:
        st.info("No hay colecciones registradas.")
    else:
        cols = st.columns(min(4, max(1, len(colecciones))))
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

    # ---- Contenido detallado del grupo ----
    coleccion_actual = st.session_state.get("coleccion_mostrando")
    if coleccion_actual and coleccion_actual in colecciones:
        st.subheader(f"Grupos de la colección: {coleccion_actual}")
        coleccion = colecciones[coleccion_actual]
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
                df = pd.DataFrame([{
                    "Nombre": a.nombre,
                    "Apellido": a.apellido,
                    "Edad": a.edad,
                    "Matrícula": a.matricula,
                    "Promedio": a.promedio
                } for a in alumnos])
                st.dataframe(df, hide_index=True)

                # ---- Agregar alumnos existentes al grupo ----
                alumnos_disponibles = []
                if "colecciones_alumnos" in st.session_state:
                    for coleccion_al in st.session_state["colecciones_alumnos"].values():
                        alumnos_disponibles.extend([a for a in coleccion_al.items if a.matricula not in [al.matricula for al in alumnos]])

                if alumnos_disponibles:
                    alumno_sel = st.selectbox(
                        f"Selecciona alumno para agregar al grupo '{g.nombre}'",
                        alumnos_disponibles,
                        format_func=lambda a: f"{a.nombre} {a.apellido} ({a.matricula})",
                        key=f"sel_alumno_{g.id}"
                    )

                    if st.button("Agregar alumno al grupo", key=f"agregar_{g.id}"):
                        g.alumnos.agregar(alumno_sel)
                        st.success("Alumno agregado al grupo.")
                        st.rerun()
                else:
                    st.info("No hay alumnos disponibles para agregar.")

        else:
            st.info("No hay grupos en esta colección.")

        # ---- Guardar colección actual como JSON ----
        if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}_grupo"):
            coleccion.guardar_como_json()
            st.success(f"Colección '{coleccion_actual}' guardada como JSON.")

        # ---- Mostrar colección actual como diccionario JSON visual ----
        if st.button("Mostrar colección como diccionario", key=f"mostrar_dict_{coleccion_actual}_grupo"):
            st.subheader(f"Diccionario JSON de la colección '{coleccion_actual}'")
            diccionario = coleccion.convADiccionario()
            st.json(diccionario)

        # ---- Ocultar grupos de la colección actual ----
        if st.button("Ocultar grupos"):
            st.session_state["coleccion_mostrando"] = None
