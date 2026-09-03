# Calendario de Turnos — Peluquería

Sistema 100% local para gestionar turnos de peluquería. Sin nube, sin dependencias externas.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + Uvicorn |
| Base de datos | SQLite (WAL mode) |
| Frontend | HTML + JS vanilla |
| Contenedores | Docker + Docker Compose |
| Auth | JWT |

## Inicio rápido

```bash
# Clonar / copiar este directorio
cd calendario-turnos

# Iniciar (construye imagen, levanta contenedores, espera healthcheck)
./start.sh
```

La aplicación estará disponible en:
- **App:** http://localhost:8080
- **API Docs (Swagger):** http://localhost:8080/docs
- **Health:** http://localhost:8080/health

## Comandos

| Comando | Descripción |
|---------|-------------|
| `./start.sh` | Construir y levantar servicios |
| `./stop.sh` | Detener servicios |
| `./logs.sh` | Ver logs en vivo |
| `./backup.sh` | Backup manual de la BD |
| `./reset.sh` | Reset total (elimina datos) |

## Variables de entorno

Copiar `.env.example` a `.env` y ajustar:

```bash
cp .env.example .env
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | (placeholder) | Clave secreta JWT — **cambiar en producción** |
| `TZ` | America/Argentina/Buenos_Aires | Zona horaria |
| `APP_PORT` | 8080 | Puerto en el host |
| `LOG_LEVEL` | info | Nivel de log |
| `BACKUP_HOUR` | 3 | Hora del backup automático |
| `BACKUP_MINUTE` | 0 | Minuto del backup automático |
| `RECORDATORIO_INTERVAL` | 60 | Segundos entre verificación de recordatorios |

## Volúmenes persistentes

| Volumen | Contenido | Path en contenedor |
|---------|-----------|-------------------|
| `calendario-db-data` | SQLite DB | `/app/data` |
| `calendario-backup-data` | Backups | `/app/backups` |

Los datos sobreviven a reinicios de contenedor. Para eliminarlos: `docker compose down -v`.

## Estructura del proyecto

```
calendario-turnos/
├── docker-compose.yml      # Servicios Docker
├── Dockerfile              # Imagen Python
├── requirements.txt        # Dependencias Python
├── .env.example            # Variables de entorno (template)
├── .env                    # Variables de entorno (local)
├── .dockerignore           # Archivos excluidos de la imagen
├── start.sh                # Script de inicio
├── stop.sh                 # Script de detención
├── logs.sh                 # Ver logs
├── backup.sh               # Backup manual
├── reset.sh                # Reset total
├── app/
│   ├── main.py             # FastAPI app (stub)
│   └── static/             # Frontend estático
├── data/                   # SQLite DB (volumen)
└── backups/                # Backups (volumen)
```

## Seguridad

- JWT con expiración de 8h
- Usuario no-root en contenedor
- Healthcheck automático
- Logs rotados (10m max, 3 archivos)

## Backup

El backup automático corre diariamente a la hora configurada (`BACKUP_HOUR`).
Para backup manual: `./backup.sh`

Los backups se guardan en `backups/turnos_YYYYMMDD_HHMMSS.db`.

## Roadmap

- [x] Infraestructura Docker
- [ ] CRUD completo (peluqueros, servicios, clientes)
- [ ] Sistema de turnos con validación de solapamiento
- [ ] Agenda día/semana
- [ ] Recordatorios automáticos
- [ ] Panel administrativo
- [ ] Export CSV/PDF

## Licencia

Uso interno — Peluquería.
