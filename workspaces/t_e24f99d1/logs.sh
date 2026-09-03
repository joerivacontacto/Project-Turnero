#!/usr/bin/env bash
# ============================================================
# Calendario de Turnos — Logs en vivo (logs.sh)
# ============================================================
# Uso: ./logs.sh [servicio]
# Ejemplo: ./logs.sh app
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SERVICE="${1:-app}"
docker compose logs -f "$SERVICE"
