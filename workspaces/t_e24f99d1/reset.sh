#!/usr/bin/env bash
# ============================================================
# Calendario de Turnos — Reset total (reset.sh)
# ============================================================
# Uso: ./reset.sh
# ⚠️  ELIMINA todos los datos (volúmenes incluidos)
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "⚠️  ADVERTENCIA: Esto eliminará TODOS los datos."
echo "¿Estás seguro? (escribí 'si' para confirmar): "
read -r CONFIRM

if [ "$CONFIRM" != "si" ]; then
    echo "Cancelado."
    exit 0
fi

echo "[INFO] Deteniendo servicios y eliminando volúmenes..."
docker compose down -v

echo "[OK] Reset completo. Los datos fueron eliminados."
echo "Para empezar de nuevo: ./start.sh"
