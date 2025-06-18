from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import streamlit as st
import threading
import time
import os


class DBManager:
    _instance = None
    COLA_ARCHIVO = "cola_guardado.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.connected = False
            cls._instance.cola_guardado = {}
            cls._instance.timer_activo = False
            cls._instance.cargar_cola_desde_archivo()
        return cls._instance

    def cargar_cola_desde_archivo(self):
        try:
            if os.path.exists(self.COLA_ARCHIVO):
                with open(self.COLA_ARCHIVO, "r", encoding="utf-8") as f:
                    cola_data = json.load(f)
                    self.cola_guardado = cola_data
                    print(f"Cola cargada desde archivo: {len(self.cola_guardado)} clases pendientes")
            else:
                self.cola_guardado = {}
                print("No se encontró archivo de cola, iniciando con cola vacía")
        except Exception as e:
            print(f"Error al cargar cola desde archivo: {e}")
            self.cola_guardado = {}

    def guardar_cola_en_archivo(self):
        try:
            with open(self.COLA_ARCHIVO, "w", encoding="utf-8") as f:
                json.dump(self.cola_guardado, f, indent=4, ensure_ascii=False)
            print(f"Cola guardada en archivo: {len(self.cola_guardado)} clases")
        except Exception as e:
            print(f"Error al guardar cola en archivo: {e}")

    def limpiar_cola(self):
        self.cola_guardado = {}
        self.guardar_cola_en_archivo()
        print("Cola limpiada completamente")

    def obtener_estado_cola(self):
        return {
            "total_clases": len(self.cola_guardado),
            "clases": list(self.cola_guardado.keys())
        }

    def intentar_conexion(self):
        try:
            print("Intentando conectar a MongoDB...")
            uri = "mongodb+srv://sau:871212@cluster0.rwlvrjg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            self.db = self.client.escuela
            self.connected = True
            return True
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            self.connected = False
            return False

    def crear_coleccion(self, nombre_coleccion):
        if not self.connected:
            return False
        try:
            if nombre_coleccion not in self.db.list_collection_names():
                self.db.create_collection(nombre_coleccion)
            return True
        except Exception:
            return False

    def guardar_datos(self, coleccion_nombre, datos, clase_nombre, append_mode=False):
        """
        Guarda datos en la base de datos

        Args:
            coleccion_nombre: Nombre de la colección
            datos: Datos a guardar (puede ser un objeto o lista)
            clase_nombre: Nombre de la clase
            append_mode: Si es True, agrega los datos al arreglo existente.
                        Si es False, reemplaza todos los datos
        """
        if self.intentar_conexion():
            try:
                self.procesar_cola()
                coleccion = self.db[coleccion_nombre]

                if append_mode:
                    # Modo agregar: añade nuevos datos al arreglo existente
                    documento_existente = coleccion.find_one({"clase": clase_nombre})

                    if documento_existente:
                        # Si existe, agrega los nuevos datos al arreglo
                        datos_existentes = documento_existente.get("datos", [])
                        if isinstance(datos, list):
                            datos_existentes.extend(datos)
                        else:
                            datos_existentes.append(datos)
                        datos_finales = datos_existentes
                    else:
                        # Si no existe, crea el arreglo
                        datos_finales = datos if isinstance(datos, list) else [datos]

                    documento = {
                        "clase": clase_nombre,
                        "datos": datos_finales
                    }
                    coleccion.replace_one({"clase": clase_nombre}, documento, upsert=True)
                else:
                    # Modo reemplazar: guarda los datos tal como vienen
                    datos_finales = datos if isinstance(datos, list) else [datos]
                    documento = {
                        "clase": clase_nombre,
                        "datos": datos_finales
                    }
                    coleccion.replace_one({"clase": clase_nombre}, documento, upsert=True)

                print(f"Guardado en MongoDB: {clase_nombre} ({len(datos_finales)} registros)")

                # Limpia de la cola si estaba pendiente
                if clase_nombre in self.cola_guardado:
                    del self.cola_guardado[clase_nombre]
                    self.guardar_cola_en_archivo()
                return True

            except Exception as e:
                print(f"Error al guardar en MongoDB: {e}")
                self.connected = False

        # Si falla la conexión, agrega a la cola
        self.agregar_a_cola(coleccion_nombre, datos, clase_nombre, append_mode)
        self.guardar_json_local(datos, clase_nombre)
        self.iniciar_timer()
        return False

    def agregar_a_cola(self, coleccion_nombre, datos, clase_nombre, append_mode=False):
        # Asegura que los datos estén en formato de arreglo
        datos_array = datos if isinstance(datos, list) else [datos]

        self.cola_guardado[clase_nombre] = {
            "coleccion": coleccion_nombre,
            "datos": datos_array,
            "clase": clase_nombre,
            "append_mode": append_mode,
            "timestamp": time.time()
        }
        self.guardar_cola_en_archivo()
        print(f"Agregado a la cola: {clase_nombre} ({len(datos_array)} registros)")

    def guardar_json_local(self, datos, clase_nombre):
        nombre_archivo = f"{clase_nombre}.json"
        # Asegura que se guarde como arreglo
        datos_array = datos if isinstance(datos, list) else [datos]

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos_array, f, indent=4, ensure_ascii=False)
        print(f"Guardado local: {nombre_archivo} ({len(datos_array)} registros)")

    def iniciar_timer(self):
        if not self.timer_activo:
            self.timer_activo = True
            timer = threading.Timer(20.0, self.intentar_subir_cola)
            timer.start()

    def intentar_subir_cola(self):
        self.timer_activo = False
        if not self.cola_guardado:
            return
        if self.intentar_conexion():
            self.procesar_cola()
        else:
            print("Reintentando subir en 20 segundos...")
            self.iniciar_timer()

    def procesar_cola(self):
        if not self.cola_guardado:
            return

        clases_procesadas = []
        for clase_nombre, item in self.cola_guardado.items():
            try:
                self.crear_coleccion(item["coleccion"])
                coleccion = self.db[item["coleccion"]]

                append_mode = item.get("append_mode", False)
                datos = item["datos"]

                if append_mode:
                    # Modo agregar: añade al arreglo existente
                    documento_existente = coleccion.find_one({"clase": item["clase"]})

                    if documento_existente:
                        datos_existentes = documento_existente.get("datos", [])
                        datos_existentes.extend(datos)
                        datos_finales = datos_existentes
                    else:
                        datos_finales = datos
                else:
                    # Modo reemplazar
                    datos_finales = datos

                documento = {
                    "clase": item["clase"],
                    "datos": datos_finales
                }

                coleccion.replace_one({"clase": item["clase"]}, documento, upsert=True)
                clases_procesadas.append(clase_nombre)
                print(f"Subido desde cola: {item['clase']} ({len(datos_finales)} registros)")

            except Exception as e:
                print(f"Error al subir {item['clase']}: {e}")
                break

        # Limpia las clases procesadas de la cola
        for clase_nombre in clases_procesadas:
            del self.cola_guardado[clase_nombre]

        if clases_procesadas:
            self.guardar_cola_en_archivo()

        if not self.cola_guardado:
            print("Cola procesada completamente")
        else:
            print(f"Quedan {len(self.cola_guardado)} clases en la cola")

    def cargar_datos(self, coleccion_nombre, clase_nombre):
        if not self.connected:
            return None
        try:
            coleccion = self.db[coleccion_nombre]
            documento = coleccion.find_one({"clase": clase_nombre})
            return documento["datos"] if documento else None
        except Exception:
            return None

    def agregar_registro(self, coleccion_nombre, nuevo_registro, clase_nombre):
        """
        Método específico para agregar un solo registro al arreglo existente
        """
        return self.guardar_datos(coleccion_nombre, nuevo_registro, clase_nombre, append_mode=True)

    def reemplazar_todos_datos(self, coleccion_nombre, nuevos_datos, clase_nombre):
        """
        Método específico para reemplazar todos los datos de una clase
        """
        return self.guardar_datos(coleccion_nombre, nuevos_datos, clase_nombre, append_mode=False)

    def obtener_estadisticas_cola(self):
        """
        Devuelve estadísticas detalladas de la cola
        """
        total_registros = 0
        estadisticas = {}

        for clase_nombre, item in self.cola_guardado.items():
            num_registros = len(item.get("datos", []))
            total_registros += num_registros
            estadisticas[clase_nombre] = {
                "registros": num_registros,
                "timestamp": item.get("timestamp", 0),
                "modo": "agregar" if item.get("append_mode", False) else "reemplazar"
            }

        return {
            "total_clases": len(self.cola_guardado),
            "total_registros": total_registros,
            "detalles": estadisticas
        }

    def mostrar_estado_conexion(self):
        if self.connected:
            st.success("✅ Conectado a MongoDB")
        else:
            estadisticas = self.obtener_estadisticas_cola()
            total_clases = estadisticas["total_clases"]
            total_registros = estadisticas["total_registros"]

            if total_clases > 0:
                st.warning(
                    f"⚠️ Sin conexión a MongoDB - Cola: {total_clases} clases, {total_registros} registros pendientes")

                with st.expander("Ver detalles de la cola"):
                    for clase_nombre, detalles in estadisticas["detalles"].items():
                        timestamp = detalles["timestamp"]
                        tiempo_formateado = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                        modo = detalles["modo"]
                        registros = detalles["registros"]

                        st.text(f"• {clase_nombre}: {registros} registros, modo: {modo}")
                        st.text(f"  Agregado: {tiempo_formateado}")
                        st.text("")

                    col1, col2 = st.columns(2)
                    if col1.button("🔄 Intentar subir cola"):
                        if self.intentar_conexion():
                            self.procesar_cola()
                            st.rerun()
                        else:
                            st.error("No se pudo conectar a MongoDB")

                    if col2.button("🗑️ Limpiar cola"):
                        self.limpiar_cola()
                        st.success("Cola limpiada")
                        st.rerun()
            else:
                st.warning("⚠️ Sin conexión a MongoDB")

    def cerrar_conexion(self):
        if self.client:
            self.client.close()
            self.connected = False