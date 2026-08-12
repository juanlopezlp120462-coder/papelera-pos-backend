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
        # Configurar token de GitHub para evitar el error 403 (Rate Limit)
        headers = {}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        respuesta = requests.get(
            "https://api.github.com/repos/juanlopezlp120462-coder/papelera-pos-desktop/releases/latest",
            headers=headers,
            timeout=10
        )

        respuesta.raise_for_status()

        release = respuesta.json()

        version = release["tag_name"].replace("v", "")

        url_update = None

        for archivo in release.get("assets", []):

            nombre = archivo.get("name", "").lower()

            if nombre.endswith(".zip"):
                url_update = archivo.get("browser_download_url")
                break

        if not url_update:
            return {
                "version": version,
                "mensaje": "No se encontró archivo ZIP",
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