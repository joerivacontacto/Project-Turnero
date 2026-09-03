#!/usr/bin/env bash
# ============================================================
# Calendario de Turnos — Script de inicio (start.sh)
# ============================================================
# Uso: ./start.sh
# Requisitos: docker, docker compose
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Verificar prerequisitos ---
log "Verificando prerequisitos..."
if ! command -v docker &> /dev/null; then
    err "Docker no está instalado. Instalalo desde https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    err "Docker Compose no está disponible. Necesitás Docker Compose v2+."
    exit 1
fi
ok "Docker y Docker Compose disponibles"

# --- Crear .env si no existe ---
if [ ! -f .env ]; then
    log "Creando .env desde .env.example..."
    cp .env.example .env
    warn "⚠️  Recordá cambiar JWT_SECRET_KEY en .env antes de usar en producción"
fi
ok ".env presente"

# --- Crear directorios de volúmenes ---
mkdir -p data backups
ok "Directorios data/ y backups/ listos"

# --- Construir y levantar ---
log "Construyendo imagen Docker..."
docker compose build --no-cache

log "Levantando servicios..."
docker compose up -d

# --- Esperar healthcheck ---
log "Esperando que la aplicación esté lista..."
MAX_RETRIES=30
RETRY=0
until docker compose exec -T app curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        err "La aplicación no respondió en ${MAX_RETRIES} intentos."
        err "Verificá los logs: docker compose logs app"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""

# --- Mostrar estado ---
ok "¡Calendario de Turnos corriendo!"
echo ""
echo -e "  ${GREEN}App:${NC}        http://localhost:$(grep APP_PORT .env | cut -d= -f2 || echo 8080)"
echo -e "  ${GREEN}API Docs:${NC}   http://localhost:$(grep APP_PORT .env | cut -d= -f2 || echo 8080)/docs"
echo -e "  ${GREEN}Health:${NC}     http://localhost:$(grep APP_PORT .env | cut -d= -f2 || echo 8080)/health"
echo ""
echo "Comandos útiles:"
echo "  docker compose logs -f app    # Ver logs"
echo "  docker compose down           # Detener"
echo "  docker compose restart app    # Reiniciar"
echo "  ./backup.sh                   # Backup manual"
