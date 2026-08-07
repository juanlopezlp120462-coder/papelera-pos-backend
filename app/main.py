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
    return {
        "version": "1.0.8",
        "mensaje": "Papelera POS actualizado",
        "url": "https://github.com/juanlopezlp120462-coder/papelera-pos-backend/releases/download/v1.0.8/UPDATE.zip"
    }

# CORS abierto: así el celular y la PC (o cualquier dispositivo) pueden
# consumir la API sin bloqueos del navegador. Cuando tengas el dominio
# final del frontend, podés restringir allow_origins a esa URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(caja.router)
app.include_router(pedidos.router)
app.include_router(configuracion.router)


@app.get("/")
def raiz():
    return {"status": "ok", "mensaje": "API de Papelera POS funcionando"}
