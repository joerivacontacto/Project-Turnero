from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_schema, get_connection
from app.routes import auth, peluqueros, servicios, clientes, turnos, agenda, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_connection()
    init_schema(conn)
    yield

app = FastAPI(
    title="Calendario de Turnos API",
    description="API REST para gestión de turnos de peluquería",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(peluqueros.router)
app.include_router(servicios.router)
app.include_router(clientes.router)
app.include_router(turnos.router)
app.include_router(agenda.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "app": "Calendario de Turnos",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {"status": "ok"}
