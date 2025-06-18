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
            cls._instance.cola_guardado = []
            cls._instance.timer_activo = False
            cls._instance.cargar_cola_desde_archivo()
        return cls._instance

    def cargar_cola_desde_archivo(self):
        try:
            if os.path.exists(self.COLA_ARCHIVO):
                with open(self.COLA_ARCHIVO, "r", encoding="utf-8") as f:
                    cola_data = json.load(f)
                    if isinstance(cola_data, dict):
                        self.cola_guardado = list(cola_data.values())
                    else:
                        self.cola_guardado = cola_data
            else:
                self.cola_guardado = []
        except Exception:
            self.cola_guardado = []

    def guardar_cola_en_archivo(self):
        try:
            with open(self.COLA_ARCHIVO, "w", encoding="utf-8") as f:
                json.dump(self.cola_guardado, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def limpiar_cola(self):
        self.cola_guardado = []
        self.guardar_cola_en_archivo()

    def obtener_info_cola(self):
        total_registros = 0
        clases = []
        for item in self.cola_guardado:
            num_registros = len(item.get("datos", []))
            total_registros += num_registros
            clases.append(item.get("clase", "Desconocido"))
        return {
            "total_elementos": len(self.cola_guardado),
            "total_registros": total_registros,
            "clases": clases
        }

    def intentar_conexion(self):
        try:
            uri = "mongodb+srv://sau:871212@cluster0.rwlvrjg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            self.db = self.client.escuela
            self.connected = True
            return True
        except Exception:
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
        if self.intentar_conexion():
            try:
                self.procesar_cola()
                coleccion = self.db[coleccion_nombre]
                datos_array = datos if isinstance(datos, list) else [datos]
                if not append_mode:
                    coleccion.delete_many({"clase": clase_nombre})
                documentos_a_insertar = []
                for item in datos_array:
                    documento = item.copy()
                    documento["clase"] = clase_nombre
                    documentos_a_insertar.append(documento)
                if documentos_a_insertar:
                    coleccion.insert_many(documentos_a_insertar)
                self.cola_guardado = [item for item in self.cola_guardado if item.get("clase") != clase_nombre]
                self.guardar_cola_en_archivo()
                return True
            except Exception:
                self.connected = False
        self.agregar_a_cola(coleccion_nombre, datos, clase_nombre, append_mode)
        self.guardar_json_local(datos, clase_nombre)
        self.iniciar_timer()
        return False

    def agregar_a_cola(self, coleccion_nombre, datos, clase_nombre, append_mode=False):
        datos_array = datos if isinstance(datos, list) else [datos]
        self.cola_guardado = [item for item in self.cola_guardado if item.get("clase") != clase_nombre]
        nueva_entrada = {
            "coleccion": coleccion_nombre,
            "datos": datos_array,
            "clase": clase_nombre,
            "append_mode": append_mode,
            "timestamp": time.time()
        }
        self.cola_guardado.append(nueva_entrada)
        self.guardar_cola_en_archivo()

    def guardar_json_local(self, datos, clase_nombre):
        nombre_archivo = f"{clase_nombre}.json"
        datos_array = datos if isinstance(datos, list) else [datos]
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos_array, f, indent=4, ensure_ascii=False)

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
            self.iniciar_timer()

    def procesar_cola(self):
        if not self.cola_guardado:
            return
        elementos_procesados = []
        for i, item in enumerate(self.cola_guardado):
            try:
                self.crear_coleccion(item["coleccion"])
                coleccion = self.db[item["coleccion"]]
                clase_nombre = item["clase"]
                datos = item["datos"]
                append_mode = item.get("append_mode", False)
                if not append_mode:
                    coleccion.delete_many({"clase": clase_nombre})
                documentos_a_insertar = []
                for registro in datos:
                    documento = registro.copy()
                    documento["clase"] = clase_nombre
                    documentos_a_insertar.append(documento)
                if documentos_a_insertar:
                    coleccion.insert_many(documentos_a_insertar)
                elementos_procesados.append(i)
            except Exception:
                break
        for i in reversed(elementos_procesados):
            del self.cola_guardado[i]
        if elementos_procesados:
            self.guardar_cola_en_archivo()

    def cargar_datos(self, coleccion_nombre, clase_nombre):
        if not self.connected:
            return None
        try:
            coleccion = self.db[coleccion_nombre]
            documentos = list(coleccion.find({"clase": clase_nombre}))
            if documentos:
                datos_limpios = []
                for doc in documentos:
                    doc.pop('_id', None)
                    doc.pop('clase', None)
                    datos_limpios.append(doc)
                return datos_limpios
            return None
        except Exception:
            return None

    def agregar_registro(self, coleccion_nombre, nuevo_registro, clase_nombre):
        return self.guardar_datos(coleccion_nombre, nuevo_registro, clase_nombre, append_mode=True)

    def reemplazar_todos_datos(self, coleccion_nombre, nuevos_datos, clase_nombre):
        return self.guardar_datos(coleccion_nombre, nuevos_datos, clase_nombre, append_mode=False)

    def obtener_estadisticas_cola(self):
        total_registros = 0
        estadisticas = {}
        for item in self.cola_guardado:
            clase_nombre = item.get("clase", "Desconocido")
            num_registros = len(item.get("datos", []))
            total_registros += num_registros
            estadisticas[clase_nombre] = {
                "registros": num_registros,
                "timestamp": item.get("timestamp", 0),
                "modo": "agregar" if item.get("append_mode", False) else "reemplazar"
            }
        return {
            "total_elementos": len(self.cola_guardado),
            "total_registros": total_registros,
            "detalles": estadisticas
        }

    def mostrar_estado_conexion(self):
        if self.connected:
            st.success("✅ Conectado a MongoDB")
        else:
            estadisticas = self.obtener_estadisticas_cola()
            total_elementos = estadisticas["total_elementos"]
            total_registros = estadisticas["total_registros"]
            if total_elementos > 0:
                st.warning(f"⚠️ Sin conexión a MongoDB - Cola: {total_elementos} elementos, {total_registros} registros pendientes")
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
