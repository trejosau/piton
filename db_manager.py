from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import streamlit as st
import threading
import time
import os


class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.connected = False
            cls._instance.cola_guardado = []
            cls._instance.timer_activo = False
        return cls._instance

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

    def guardar_datos(self, coleccion_nombre, datos, clase_nombre):
        if self.intentar_conexion():
            try:
                self.procesar_cola()


                coleccion = self.db[coleccion_nombre]
                documento = {
                    "clase": clase_nombre,
                    "datos": datos
                }
                coleccion.replace_one({"clase": clase_nombre}, documento, upsert=True)
                print(f"Guardado en MongoDB: {clase_nombre}")
                return True
            except Exception as e:
                print(f"Error al guardar en MongoDB: {e}")
                self.connected = False

        self.agregar_a_cola(coleccion_nombre, datos, clase_nombre)
        self.guardar_json_local(datos, clase_nombre)
        self.iniciar_timer()
        return False

    def agregar_a_cola(self, coleccion_nombre, datos, clase_nombre):
        for i, item in enumerate(self.cola_guardado):
            if item["clase"] == clase_nombre:
                self.cola_guardado[i] = {
                    "coleccion": coleccion_nombre,
                    "datos": datos,
                    "clase": clase_nombre
                }
                return

        self.cola_guardado.append({
            "coleccion": coleccion_nombre,
            "datos": datos,
            "clase": clase_nombre
        })

    def guardar_json_local(self, datos, clase_nombre):
        nombre_archivo = f"{clase_nombre}.json"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print(f"Guardado local: {nombre_archivo}")

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

        elementos_procesados = []

        for item in self.cola_guardado:
            try:
                self.crear_coleccion(item["coleccion"])
                coleccion = self.db[item["coleccion"]]
                documento = {
                    "clase": item["clase"],
                    "datos": item["datos"]
                }
                coleccion.replace_one({"clase": item["clase"]}, documento, upsert=True)
                elementos_procesados.append(item)
                print(f"Subido desde cola: {item['clase']}")
            except Exception as e:
                print(f"Error al subir {item['clase']}: {e}")
                break

        for item in elementos_procesados:
            self.cola_guardado.remove(item)

        if not self.cola_guardado:
            print("Cola procesada completamente")

    def cargar_datos(self, coleccion_nombre, clase_nombre):
        if not self.connected:
            return None
        try:
            coleccion = self.db[coleccion_nombre]
            documento = coleccion.find_one({"clase": clase_nombre})
            return documento["datos"] if documento else None
        except Exception:
            return None

    def mostrar_estado_conexion(self):
        if self.connected:
            st.success("Conectado a MongoDB")
        else:
            st.warning(f"Sin conexión a MongoDB - Cola pendiente: {len(self.cola_guardado)} elementos")

    def cerrar_conexion(self):
        if self.client:
            self.client.close()
            self.connected = False