FROM python:3.11-slim

# ============================================================
# Calendario de Turnos — Imagen de producción local
# ============================================================

LABEL maintainer="DevOps <gaston>"
LABEL description="Calendario de Turnos Peluquería — FastAPI + SQLite"

# Evitar .pyc y habilitar logging en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python (capa cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la aplicación
COPY app/ ./app/

# Directorios para volúmenes persistentes
RUN mkdir -p /app/data /app/backups

# Healthcheck integrado en la imagen
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Usuario no-root para seguridad
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Comando de inicio — Uvicorn sirve FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
