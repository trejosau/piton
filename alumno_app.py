import streamlit as st
import json
import pandas as pd
from alumno import Alumno

def render(colecciones):
    st.header("Colecciones de Alumnos")

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
                    items_ok = hasattr(alumnos_cargados, "items") and isinstance(alumnos_cargados.items, list) and alumnos_cargados.items
                    if resultado is False or not items_ok:
                        st.error("El archivo no corresponde a una colección válida de alumnos. Usa un JSON de alumnos válido.")
                    else:
                        colecciones[nombre_col] = alumnos_cargados
                        st.success(f"Colección '{nombre_col}' cargada con {len(alumnos_cargados.items)} alumnos.")
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
                        background: #262730;
                        color: #fff;
                        border: 2.5px solid #585858;
                        border-radius: 20px;
                        text-align: center;
                    '>
                        <div style="font-size:1.15em; font-weight:600; margin-bottom:2px;">Colección: {nombre}</div>
                        <div style="font-size:.93em; opacity:0.8;">Alumnos: <span style="font-weight:700;">{len(coleccion.items)}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar alumnos", key=f"mostrar_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    # ---- Mostrar tabla y CRUD de alumnos ----
    coleccion_actual = st.session_state.get("coleccion_mostrando")
    if coleccion_actual:
        st.subheader(f"Alumnos de la colección: {coleccion_actual}")
        coleccion = colecciones[coleccion_actual]
        alumnos = getattr(coleccion, "items", [])

        # Tabla de alumnos existentes
        if alumnos:
            df = pd.DataFrame([{
                "Nombre": al.nombre,
                "Apellido": al.apellido,
                "Edad": al.edad,
                "Matrícula": al.matricula,
                "Promedio": al.promedio
            } for al in alumnos])
            st.dataframe(df, hide_index=True)

            # Editar o eliminar alumnos existentes
            st.markdown("### Editar o eliminar alumnos")
            for idx, al in enumerate(alumnos):
                cols = st.columns([2, 2, 1, 2, 2, 1, 1])
                nuevo_nombre = cols[0].text_input("Nombre", al.nombre, key=f"edit_nombre_{al.matricula}")
                nuevo_apellido = cols[1].text_input("Apellido", al.apellido, key=f"edit_apellido_{al.matricula}")
                nueva_edad = cols[2].number_input("Edad", 0, 120, al.edad, key=f"edit_edad_{al.matricula}")
                nueva_matricula = cols[3].number_input("Matrícula", min_value=23170, value=al.matricula, key=f"edit_matricula_{al.matricula}")
                nuevo_promedio = cols[4].number_input("Promedio", 0.0, 10.0, al.promedio, step=0.1, key=f"edit_prom_{al.matricula}")

                if cols[5].button("Guardar", key=f"save_{al.matricula}"):
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

                if cols[6].button("Eliminar", key=f"del_{al.matricula}"):
                    coleccion.eliminar(al.matricula)
                    st.warning("Alumno eliminado.")
                    st.rerun()
        else:
            st.info("No hay alumnos en esta colección.")

        # ---- Formulario para agregar un alumno nuevo a la colección ----
        st.markdown("### Agregar nuevo alumno a esta colección")
        with st.form(f"agregar_alumno_{coleccion_actual}"):
            nombre = st.text_input("Nombre del alumno")
            apellido = st.text_input("Apellido del alumno")
            edad = st.number_input("Edad del alumno", min_value=0, max_value=120, value=18)
            matricula = st.number_input("Matrícula del alumno", min_value=23170)
            promedio = st.number_input("Promedio del alumno", min_value=0.0, max_value=10.0, step=0.1, value=8.0)

            agregar_alumno = st.form_submit_button("Agregar Alumno")
            if agregar_alumno:
                if nombre and apellido and matricula:
                    matriculas_existentes = [al.matricula for al in alumnos]
                    if matricula in matriculas_existentes:
                        st.error("La matrícula ya existe en esta colección. Debe ser única.")
                    else:
                        nuevo_alumno = Alumno(nombre, apellido, edad, matricula, promedio)
                        coleccion.agregar(nuevo_alumno)
                        st.success(f"Alumno {nombre} agregado correctamente.")
                        st.rerun()
                else:
                    st.warning("Por favor, completa todos los campos obligatorios.")

        # Guardar colección actual como JSON
        if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}"):
            coleccion.guardar_como_json()
            st.success(f"Colección '{coleccion_actual}' guardada como JSON.")

        # Mostrar colección como diccionario JSON visual
        if st.button("Mostrar colección como diccionario", key=f"mostrar_dict_{coleccion_actual}_alumno"):
            st.subheader(f"Diccionario JSON de la colección '{coleccion_actual}'")
            diccionario = coleccion.convADiccionario()
            st.json(diccionario)

        # Ocultar alumnos de la colección actual
        if st.button("Ocultar alumnos"):
            st.session_state["coleccion_mostrando"] = None
