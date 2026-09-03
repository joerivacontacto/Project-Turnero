"""
Calendario de Turnos — Aplicación principal (FastAPI)
=====================================================
Este es un stub mínimo para validar la infraestructura Docker.
El backend completo se implementa en la fase de desarrollo (t_1ddf4a95).
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Calendario de Turnos Peluquería",
    description="Sistema de gestión de turnos — 100% local",
    version="0.1.0",
)


@app.get("/health", tags=["sistema"])
async def healthcheck():
    """Healthcheck para Docker y monitoreo."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "calendario-turnos",
            "version": "0.1.0",
        },
    )


@app.get("/", tags=["sistema"])
async def root():
    """Endpoint raíz — información básica."""
    return {
        "app": "Calendario de Turnos Peluquería",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
