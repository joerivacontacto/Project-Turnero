#!/usr/bin/env bash
# ============================================================
# Calendario de Turnos — Script de detención (stop.sh)
# ============================================================
# Uso: ./stop.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[INFO] Deteniendo servicios..."
docker compose down

echo "[OK] Servicios detenidos. Los datos se conservan en los volúmenes."
echo "Para eliminar todo (incluyendo datos): docker compose down -v"
