from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import streamlit as st


class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.connected = False
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
        if not self.connected:
            return False
        try:
            coleccion = self.db[coleccion_nombre]
            documento = {
                "clase": clase_nombre,
                "datos": datos
            }
            coleccion.replace_one({"clase": clase_nombre}, documento, upsert=True)
            return True
        except Exception:
            return False

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
            st.warning("Sin conexión a MongoDB - usando archivos locales")

    def cerrar_conexion(self):
        if self.client:
            self.client.close()
            self.connected = False