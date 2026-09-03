#!/usr/bin/env bash
# ============================================================
# Calendario de Turnos — Backup manual (backup.sh)
# ============================================================
# Uso: ./backup.sh
# Crea un backup timestamped de la BD SQLite en backups/
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/turnos_${TIMESTAMP}.db"

echo "[INFO] Creando backup: $BACKUP_FILE"

# Si el contenedor está corriendo, usar sqlite3 dentro del contenedor
if docker compose ps --format '{{.Name}}' | grep -q "calendario-turnos"; then
    docker compose exec -T app python -c "
import sqlite3
import shutil
shutil.copy2('/app/data/turnos.db', '/app/backups/turnos_${TIMESTAMP}.db')
print('Backup creado dentro del contenedor')
"
    # Copiar del volumen al host
    docker compose cp app:/app/backups/turnos_${TIMESTAMP}.db "$BACKUP_FILE" 2>/dev/null || true
else
    # Backup directo del volumen
    if [ -f data/turnos.db ]; then
        cp data/turnos.db "$BACKUP_FILE"
    else
        echo "[ERROR] No se encontró la base de datos. ¿Está el volumen inicializado?"
        exit 1
    fi
fi

echo "[OK] Backup creado: $BACKUP_FILE"
echo "[INFO] Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
