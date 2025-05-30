import streamlit as st
import json
import pandas as pd
from alumno import Alumno
from grupo import Grupo
from maestro import Maestro

st.set_page_config(page_title="Colecciones Escolares", layout="wide")
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
colecciones = st.session_state[colecciones_key]

if "coleccion_mostrando_alumnos" not in st.session_state:
    st.session_state["coleccion_mostrando_alumnos"] = None
if "coleccion_mostrando_maestros" not in st.session_state:
    st.session_state["coleccion_mostrando_maestros"] = None

if tipo == "Alumnos":
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
        alumnos = getattr(coleccion, "items", [])

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

if tipo == "Maestros":
    st.header("Colecciones de Maestros")

    # ---- Cargar colección desde JSON ----
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
                    maestros_cargados.instanciar(data)
                    items_ok = hasattr(maestros_cargados, "items") and isinstance(maestros_cargados.items, list) and maestros_cargados.items
                    if not items_ok:
                        st.error("El archivo no contiene maestros válidos.")
                    else:
                        colecciones[nombre_col] = maestros_cargados
                        st.success(f"Colección '{nombre_col}' cargada con {len(maestros_cargados.items)} maestros.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error cargando JSON: {e}")
            else:
                st.warning("Falta archivo, nombre o ya existe una colección con ese nombre.")
    st.markdown("---")

    # ---- Agregar colección manualmente ----
    with st.form("agregar_coleccion_maestros"):
        nombre = st.text_input("Nombre de la nueva colección de maestros")
        sub = st.form_submit_button("Agregar colección")
        if sub:
            if nombre and nombre not in colecciones:
                colecciones[nombre] = Maestro()
                st.success(f"Colección '{nombre}' creada.")
                st.rerun()
            else:
                st.warning("Nombre inválido o ya existe una colección con ese nombre.")

    st.markdown("---")
    st.subheader("Colecciones de Maestros")

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
                        <div style="font-size:.93em; opacity:0.8;">Maestros: <b>{coleccion}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar maestros", key=f"mostrar_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    coleccion_actual = st.session_state.get("coleccion_mostrando")
    if coleccion_actual:
        st.subheader(f"Maestros de la colección: {coleccion_actual}")
        coleccion = colecciones[coleccion_actual]
        maestros = getattr(coleccion, "items", [])

        if maestros:
            df = pd.DataFrame([{
                "Nombre": m.nombre,
                "Apellido": m.apellido,
                "Edad": m.edad,
                "ID": m.num_maestro,
                "Especialidad": m.especialidad
            } for m in maestros])
            st.dataframe(df, hide_index=True)

            st.markdown("### Editar o eliminar maestros")
            for idx, m in enumerate(maestros):
                cols = st.columns([2, 2, 1, 2, 2, 1])
                with cols[0]:
                    nuevo_nombre = st.text_input(f"Nombre_{m.num_maestro}", m.nombre, key=f"edit_nombre_{m.num_maestro}")
                with cols[1]:
                    nuevo_apellido = st.text_input(f"Apellido_{m.num_maestro}", m.apellido, key=f"edit_apellido_{m.num_maestro}")
                with cols[2]:
                    nueva_edad = st.number_input(f"Edad_{m.num_maestro}", min_value=18, max_value=120, value=m.edad, key=f"edit_edad_{m.num_maestro}")
                with cols[3]:
                    nuevo_id = st.number_input(f"ID_{m.num_maestro}", value=int(m.num_maestro), min_value=1, step=1, key=f"edit_id_{m.num_maestro}")
                with cols[4]:
                    nueva_esp = st.text_input(f"Especialidad_{m.num_maestro}", m.especialidad, key=f"edit_esp_{m.num_maestro}")
                with cols[5]:
                    if st.button("Guardar", key=f"save_{m.num_maestro}"):
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
                if st.button("Eliminar", key=f"del_{m.num_maestro}"):
                    coleccion.eliminar(m.num_maestro)
                    st.warning("Maestro eliminado.")
                    st.rerun()
        else:
            st.info("No hay maestros en esta colección.")

        with st.form(f"agregar_maestro_{coleccion_actual}"):
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            e = st.number_input("Edad", min_value=18, max_value=120, value=30)
            i = st.number_input("ID del maestro")
            esp = st.text_input("Especialidad")
            sub_m = st.form_submit_button("Agregar maestro")
            if sub_m:
                if n and a and i and esp:
                    ids_existentes = [m.num_maestro for m in maestros]
                    if i in ids_existentes:
                        st.error("El ID ya existe en esta colección.")
                    else:
                        coleccion.agregar(Maestro(n, a, e, i, esp))
                        st.success("Maestro agregado.")
                        st.rerun()
                else:
                    st.warning("Llena todos los campos obligatorios.")

        if st.button("Ocultar maestros", key="ocultar_maestros"):
            st.session_state["coleccion_mostrando"] = None

        if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}_maestro"):
            coleccion.guardar_como_json()
            st.success(f"¡Colección '{coleccion_actual}' guardada como JSON!")

        if st.button("Mostrar en diccionario", key=f"mostrar_dict_{coleccion_actual}_maestro"):
            st.json(coleccion.convADiccionario())

# -----------------------------
#          GRUPOS
# -----------------------------
if tipo == "Grupos":
    st.header("Colecciones de Grupos")

    # Cargar colección desde archivo JSON (opcional)
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

    # Agregar nueva colección y grupo manualmente (sin alumnos aún)
    with st.form("form_nueva_coleccion_grupo"):
        nombre_coleccion = st.text_input("Nombre de la nueva colección")
        nombre_grupo = st.text_input("Nombre del grupo")

        st.markdown("#### Maestro del grupo")

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
            st.warning("Primero debes registrar maestros en el apartado de Maestros.")
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

    # Mostrar las colecciones
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
                        <div style="font-size:.93em; opacity:0.8;">Grupos: <b>{coleccion}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Mostrar grupos", key=f"mostrar_grupo_{nombre}"):
                    st.session_state["coleccion_mostrando"] = nombre

    # Mostrar contenido del grupo
    coleccion_actual = st.session_state.get("coleccion_mostrando")
    if coleccion_actual and coleccion_actual in colecciones:
        st.subheader(f"Grupos de la colección: {coleccion_actual}")
        coleccion = colecciones[coleccion_actual]

        # --- Validar que es realmente una colección de grupos ---
        items = getattr(coleccion, "items", [])
        es_arreglo_grupos = (
                hasattr(coleccion, "es_arreglo") and coleccion.es_arreglo and
                all(item.__class__.__name__ == "Grupo" for item in items)
        )

        if not es_arreglo_grupos:
            st.error(
                "Error: La colección actual no es una colección de grupos válida. Verifica cómo la creaste o cargaste.")
        else:
            grupos = items

            if grupos:
                for g in grupos:
                    maestro = getattr(g, "maestro", None)
                    if maestro is not None:
                        st.markdown(f"### Grupo: {g.nombre}")
                        st.markdown(
                            f"**Maestro:** {getattr(maestro, 'nombre', 'N/A')} {getattr(maestro, 'apellido', '')}, "
                            f"ID: {getattr(maestro, 'num_maestro', 'N/A')}, "
                            f"Especialidad: {getattr(maestro, 'especialidad', 'N/A')}"
                        )
                    else:
                        st.markdown(f"### Grupo: {g.nombre} (sin maestro asignado)")

                    st.markdown("**Alumnos:**")
                    df = pd.DataFrame([{
                        "Nombre": a.nombre,
                        "Apellido": a.apellido,
                        "Edad": a.edad,
                        "Matrícula": a.matricula,
                        "Promedio": a.promedio
                    } for a in getattr(g.alumnos, "items", [])])
                    st.dataframe(df, hide_index=True)

                    # Formulario para agregar alumno desde select de instancias existentes
                    st.markdown("### Agregar alumno existente al grupo")
                    alumnos_disponibles = []
                    if "colecciones_alumnos" in st.session_state:
                        for coleccion_al in st.session_state["colecciones_alumnos"].values():
                            if hasattr(coleccion_al, "items") and isinstance(coleccion_al.items, list):
                                alumnos_disponibles.extend(coleccion_al.items)

                    matriculas_actuales = [a.matricula for a in getattr(g.alumnos, "items", [])]
                    alumnos_para_select = [a for a in alumnos_disponibles if a.matricula not in matriculas_actuales]

                    if alumnos_para_select:
                        alumno_sel = st.selectbox(
                            "Selecciona un alumno para agregar",
                            alumnos_para_select,
                            format_func=lambda a: f"{a.nombre} {a.apellido} (Matrícula: {a.matricula})",
                            key=f"select_alumno_{g.id}"
                        )
                    else:
                        alumno_sel = None
                        st.info("No hay alumnos disponibles o todos ya están en este grupo.")

                    agregar = st.button("Agregar alumno al grupo", key=f"btn_add_alumno_{g.id}")

                    if agregar and alumno_sel:
                        g.alumnos.agregar(alumno_sel)
                        st.success("Alumno agregado al grupo.")
                        st.rerun()

            else:
                st.info("No hay grupos en esta colección.")

            if st.button("Ocultar grupos", key="ocultar_grupos"):
                st.session_state["coleccion_mostrando"] = None

            if st.button("Guardar colección como JSON", key=f"guardar_{coleccion_actual}_grupo"):
                coleccion.guardar_como_json()
                st.success(f"¡Colección '{coleccion_actual}' guardada como JSON!")

            if st.button("Mostrar en diccionario", key=f"mostrar_dict_{coleccion_actual}_grupo"):
                if es_arreglo_grupos:
                    st.json(coleccion.convADiccionario())
                else:
                    st.error("No es posible mostrar el diccionario: Esta colección no es válida.")

