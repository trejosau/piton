import streamlit as st
import json
import pandas as pd
from maestro import Maestro

def render(colecciones):
    st.header("Colecciones de Maestros")

    # ---- Apartado para cargar colección desde JSON ----
    st.subheader("Cargar colección de maestros desde archivo JSON")
    with st.form("form_json_maestros"):
        archivo = st.file_uploader("Selecciona un archivo JSON válido de maestros", type=["json"])
        nombre_col = st.text_input("Nombre para la nueva colección de maestros")
        cargar = st.form_submit_button("Cargar colección")
        if cargar:
            if archivo and nombre_col and nombre_col not in colecciones:
                try:
                    data = json.load(archivo)
                    maestros_cargados = Maestro()
                    resultado = maestros_cargados.instanciar(data)
                    items_ok = hasattr(maestros_cargados, "items") and isinstance(maestros_cargados.items, list) and maestros_cargados.items
                    if resultado is False or not items_ok:
                        st.error("El archivo no corresponde a una colección válida de maestros.")
                    else:
                        colecciones[nombre_col] = maestros_cargados
                        st.success(f"Colección '{nombre_col}' cargada con {len(maestros_cargados.items)} maestros.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error cargando JSON: {e}")
            else:
                st.warning("Falta archivo, nombre, o el nombre ya existe.")
    st.markdown("---")

    # ---- Agregar colección manualmente ----
    with st.form("agregar_coleccion_maestros"):
        nombre = st.text_input("Nombre de la nueva colección de maestros")
        sub = st.form_submit_button("Agregar colección")
        if sub:
            if nombre and nombre not in colecciones:
                colecciones[nombre] = Maestro()  # Colección vacía
                st.success(f"Colección '{nombre}' creada.")
                st.rerun()
            else:
                st.warning("Nombre inválido o colección existente.")

    st.markdown("---")
    st.subheader("Colecciones de Maestros")

    # ---- Tarjetas de colecciones ----
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
                        width: 256px;
                        height: 128px;
                        background: #1c1c1e;
                        color: #fff;
                        border: 2.5px solid #5a5a5a;
                        border-radius: 20px;
                        text-align: center;
                    '>
                        <div style="font-size:1.15em; font-weight:600; margin-bottom:2px;">Colección: {nombre}</div>
                        <div style="font-size:.93em; opacity:0.8;">Maestros: <span style="font-weight:700;">{len(coleccion.items)}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar maestros", key=f"mostrar_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    # ---- Mostrar tabla y CRUD de maestros ----
    coleccion_actual = st.session_state.get("coleccion_mostrando")
    if coleccion_actual:
        st.subheader(f"Maestros de la colección: {coleccion_actual}")
        coleccion = colecciones[coleccion_actual]
        maestros = getattr(coleccion, "items", [])

        # Tabla de maestros existentes
        if maestros:
            df = pd.DataFrame([{
                "Nombre": m.nombre,
                "Apellido": m.apellido,
                "Edad": m.edad,
                "ID Maestro": m.num_maestro,
                "Especialidad": m.especialidad
            } for m in maestros])
            st.dataframe(df, hide_index=True)

            # CRUD maestros existentes
            st.markdown("### Editar o eliminar maestros")
            for idx, m in enumerate(maestros):
                cols = st.columns([2, 2, 1, 2, 2, 1, 1])
                nuevo_nombre = cols[0].text_input("Nombre", m.nombre, key=f"edit_nombre_{m.num_maestro}")
                nuevo_apellido = cols[1].text_input("Apellido", m.apellido, key=f"edit_apellido_{m.num_maestro}")
                nueva_edad = cols[2].number_input("Edad", 18, 120, m.edad, key=f"edit_edad_{m.num_maestro}")
                nuevo_id = cols[3].text_input("ID Maestro", m.num_maestro, key=f"edit_id_{m.num_maestro}")
                nueva_esp = cols[4].text_input("Especialidad", m.especialidad, key=f"edit_esp_{m.num_maestro}")

                if cols[5].button("Guardar", key=f"save_{m.num_maestro}"):
                    ids_existentes = [ma.num_maestro for i, ma in enumerate(maestros) if i != idx]
                    if nuevo_id in ids_existentes:
                        st.error("El ID ya existe en esta colección.")
                    else:
                        m.nombre = nuevo_nombre
                        m.apellido = nuevo_apellido
                        m.edad = nueva_edad
                        m.num_maestro = nuevo_id
                        m.especialidad = nueva_esp
                        st.success("Maestro actualizado.")
                        st.rerun()

                if cols[6].button("Eliminar", key=f"del_{m.num_maestro}"):
                    coleccion.eliminar(m.num_maestro)
                    st.warning("Maestro eliminado.")
                    st.rerun()
        else:
            st.info("No hay maestros en esta colección.")

        # ---- Agregar nuevo maestro ----
        st.markdown("### Agregar nuevo maestro a esta colección")
        with st.form(f"agregar_maestro_{coleccion_actual}"):
            nombre = st.text_input("Nombre del maestro")
            apellido = st.text_input("Apellido del maestro")
            edad = st.number_input("Edad del maestro", 18, 120, 30)
            num_maestro = st.text_input("ID del maestro")
            especialidad = st.text_input("Especialidad del maestro")

            agregar_maestro = st.form_submit_button("Agregar Maestro")
            if agregar_maestro:
                if nombre and apellido and num_maestro and especialidad:
                    ids_existentes = [ma.num_maestro for ma in maestros]
                    if num_maestro in ids_existentes:
                        st.error("El ID ya existe en esta colección. Debe ser único.")
                    else:
                        nuevo_maestro = Maestro(nombre, apellido, edad, num_maestro, especialidad)
                        coleccion.agregar(nuevo_maestro)
                        st.success(f"Maestro {nombre} agregado correctamente.")
                        st.rerun()
                else:
                    st.warning("Por favor, completa todos los campos obligatorios.")

        # Guardar colección actual como JSON
        if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}_maestro"):
            coleccion.guardar_como_json()
            st.success(f"Colección '{coleccion_actual}' guardada como JSON.")

        # Mostrar colección como diccionario JSON visual
        if st.button("Mostrar colección como diccionario", key=f"mostrar_dict_{coleccion_actual}_maestro"):
            st.subheader(f"Diccionario JSON de la colección '{coleccion_actual}'")
            diccionario = coleccion.convADiccionario()
            st.json(diccionario)

        # Ocultar maestros de la colección actual
        if st.button("Ocultar maestros"):
            st.session_state["coleccion_mostrando"] = None
