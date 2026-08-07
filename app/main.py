import json
import os

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

    archivo = os.path.join(
        os.path.dirname(__file__),
        "version.json"
    )

    with open(
        archivo,
        "r",
        encoding="utf-8"
    ) as f:
        datos = json.load(f)

    return datos


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