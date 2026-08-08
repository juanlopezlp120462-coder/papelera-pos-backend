import json
import os
import requests

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import productos, clientes, ventas, caja, pedidos, configuracion


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Papelera POS - API")


# =====================================
# VERSION DEL SISTEMA
# =====================================

@app.get("/version")
def obtener_version():

    try:
        respuesta = requests.get(
            "https://api.github.com/repos/juanlopezlp120462-coder/papelera-pos-desktop/releases/latest",
            timeout=10
        )

        respuesta.raise_for_status()

        release = respuesta.json()

        version = release["tag_name"].replace("v", "")

        url_update = None

        for archivo in release.get("assets", []):

            if archivo["name"].lower().endswith(".zip"):
                url_update = archivo["browser_download_url"]
                break


        if not url_update:
            return {
                "version": version,
                "mensaje": "No se encontró UPDATE.zip",
                "url": None
            }


        return {
            "version": version,
            "mensaje": "Papelera POS actualizado",
            "url": url_update
        }


    except Exception as e:

        return {
            "version": "0.0.0",
            "mensaje": str(e),
            "url": None
        }

    except Exception as e:

        return {
            "version": "0.0.0",
            "mensaje": str(e),
            "url": None
        }
# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# ROUTERS
# =====================================

app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(caja.router)
app.include_router(pedidos.router)
app.include_router(configuracion.router)


# =====================================
# RAIZ
# =====================================

@app.get("/")
def raiz():
    return {
        "status": "ok",
        "mensaje": "API de Papelera POS funcionando"
    }