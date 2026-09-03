# Arquitectura del Sistema — Calendario de Turnos Peluquería

**Versión:** 1.0
**Fecha:** 2026-09-01
**Autor:** Fede (Tech Lead)
**Task:** t_ff35cee7 — Definir arquitectura del sistema
**Entrada:** Documento de requerimientos (t_fa2351d0)

---

## 1. Stack tecnológico

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| **Runtime** | Python 3.11+ | Estable, ecosistema rico, sin dependencias cloud |
| **Backend** | FastAPI | Async, OpenAPI automático, validación con Pydantic, más moderno que Flask |
| **Servidor ASGI** | Uvicorn | Ligero, para producción local |
| **Base de datos** | SQLite | Cumple RN-03: archivo local, backup = copiar archivo |
| **ORM** | SQLAlchemy 2.0 | Tipado, migraciones con Alembic si se necesita |
| **Auth** | JWT (python-jose) | Sin sesiones server-side, sin dependencias externas |
| **Scheduler** | APScheduler | Recordatorios, backup automático — todo in-process |
| **Frontend** | HTML + JS vanilla + CSS | Sin frameworks pesados, cumple RN-02 (< 3s carga) |
| **Notificaciones** | Service Worker + Notification API | Push local (sin nube), requiere HTTPS o localhost |
| **Contenedores** | Docker + Docker Compose | Entorno reproducible, un solo comando para levantar |
| **Backup** | Script Python (sqlite3 .backup) | Diario, copia incremental |

---

## 2. Arquitectura del sistema

### 2.1 Diagrama de alto nivel

```
┌─────────────────────────────────────────────────────────────┐
│                      Navegador (cliente)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Agenda Web  │  │ Panel Admin  │  │  Service Worker   │  │
│  │  (HTML/JS)   │  │  (HTML/JS)   │  │ (Notification API)│  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────────┘  │
└─────────┼─────────────────┼───────────────────┼──────────────┘
          │                 │                   │
          └─────────────────┼───────────────────┘
                            │ HTTP/REST
┌───────────────────────────┴──────────────────────────────────┐
│                      FastAPI (Python)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   Rutas API (REST)                      │  │
│  │  /auth  /peluqueros  /servicios  /clientes  /turnos    │  │
│  │  /agenda  /dashboard  /recordatorios  /export          │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────┴───────────────────────────────┐  │
│  │              Servicios de negocio                      │  │
│  │  TurnoService  RecordatorioService  BackupService      │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────┴───────────────────────────────┐  │
│  │               SQLAlchemy ORM + SQLite                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              APScheduler (background)                    │  │
│  │  - Verificar recordatorios cada 60s                     │  │
│  │  - Backup diario a las 03:00                           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Patrón de capas

```
Capa 1: Presentación (HTML/CSS/JS — estáticos)
Capa 2: API (FastAPI routes — endpoints REST)
Capa 3: Servicios (TurnoService, RecordatorioService — lógica de negocio)
Capa 4: Datos (SQLAlchemy models + SQLite)
```

La validación de solapamientos, cálculo de duración, y transiciones de estado viven en la **capa de servicios**, no en los endpoints ni en el frontend.

---

## 3. Estructura del proyecto

```
calendario-turnos/
├── docker-compose.yml              # Define servicio app + volúmenes
├── Dockerfile                      # Imagen Python + dependencias
├── requirements.txt                # Dependencias Python
├── .env.example                    # Variables de entorno (copiar a .env)
├── README.md                       # Instrucciones de despliegue
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # Instancia FastAPI, middleware, startup
│   ├── config.py                   # Settings desde env vars
│   ├── database.py                 # Engine SQLite, session factory
│   │
│   ├── models/                     # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── peluquero.py
│   │   ├── servicio.py
│   │   ├── peluquero_servicio.py   # Tabla intermedia N:M
│   │   ├── horario.py              # Horas laborables por peluquero
│   │   ├── ausencia.py             # Vacaciones/ausencias
│   │   ├── cliente.py
│   │   ├── turno.py
│   │   └── recordatorio.py
│   │
│   ├── schemas/                    # Pydantic (request/response)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── peluquero.py
│   │   ├── servicio.py
│   │   ├── cliente.py
│   │   └── turno.py
│   │
│   ├── routes/                     # Endpoints FastAPI
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── peluqueros.py
│   │   ├── servicios.py
│   │   ├── clientes.py
│   │   ├── turnos.py
│   │   ├── agenda.py
│   │   └── admin.py
│   │
│   ├── services/                   # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── turno_service.py        # Crear/cancelar, validación solapamiento
│   │   ├── agenda_service.py       # Cálculo de huecos disponibles
│   │   ├── recordatorio_service.py # Envío + scheduler
│   │   └── backup_service.py       # Backup SQLite
│   │
│   ├── auth/                       # Utilidades de autenticación
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   └── permissions.py          # Decoradores de roles
│   │
│   ├── static/                     # Frontend estático
│   │   ├── index.html              # Landing / login
│   │   ├── agenda.html             # Vista día/semana
│   │   ├── admin.html              # Panel administrativo
│   │   ├── css/
│   │   │   └── main.css
│   │   ├── js/
│   │   │   ├── api.js             # Cliente fetch wrapper
│   │   │   ├── agenda.js          # Lógica vista agenda
│   │   │   ├── turnos.js          # Crear/cancelar turnos
│   │   │   └── admin.js           # Panel admin
│   │   └── sw.js                   # Service Worker (notificaciones)
│   │
│   └── utils/
│       ├── __init__.py
│       └── time.py                # Helpers de hora local
│
├── data/                          # SQLite DB (montado como volumen)
│   └── .gitkeep
│
├── backups/                       # Backups automáticos
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_turnos.py
    └── test_agenda.py
```

---

## 4. Modelo de datos

### 4.1 Entidades principales

```
┌──────────────┐       ┌───────────────────┐       ┌──────────────┐
│   USUARIO    │       │    PELUQUERO      │       │   SERVICIO   │
├──────────────┤       ├───────────────────┤       ├──────────────┤
│ id           │       │ id                │       │ id           │
│ username     │       │ nombre            │       │ nombre       │
│ password_hash│       │ activo (bool)     │       │ duracion_min │
│ rol          │       └─────────┬─────────┘       │ precio       │
│ creado_en    │                 │ N:M              │ activo       │
└──────────────┘                 │                  └──────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   PELUQUERO_SERVICIO    │
                    ├─────────────────────────┤
                    │ peluquero_id (FK)       │
                    │ servicio_id (FK)        │
                    └─────────────────────────┘

┌──────────────┐       ┌───────────────────┐       ┌─────────────────┐
│   CLIENTE    │       │      TURNO        │       │  RECORDATORIO   │
├──────────────┤       ├───────────────────┤       ├─────────────────┤
│ id           │       │ id                │       │ id              │
│ nombre       │       │ cliente_id (FK)   │       │ turno_id (FK)   │
│ telefono     │       │ peluquero_id (FK) │       │ tipo (24h/12h)  │
│ email        │       │ servicio_id (FK)  │       │ enviado_en      │
│ activo       │       │ fecha             │       │ estado          │
│ creado_en    │       │ hora_inicio       │       └─────────────────┘
└──────────────┘       │ hora_fin          │
                       │ estado            │
                       │ tolerancia_min    │
                       │ creado_en         │
                       └───────────────────┘

┌─────────────────────┐
│     HORARIO         │
├─────────────────────┤
│ id                  │
│ peluquero_id (FK)   │
│ dia_semana (0-6)    │
│ hora_inicio         │
│ hora_fin            │
└─────────────────────┘

┌─────────────────────┐
│    AUSENCIA         │
├─────────────────────┤
│ id                  │
│ peluquero_id (FK)   │
│ fecha_inicio        │
│ fecha_fin           │
│ motivo              │
└─────────────────────┘
```

### 4.2 Decisiones de diseño

- **SQLite** con `WAL` mode para mejor concurrencia (2 usuarios).
- **`hora_inicio`/`hora_fin`** almacenadas como `TEXT` en formato `HH:MM` local (cumple RN: usar hora local, no UTC).
- **`fecha`** almacenada como `TEXT` en formato `YYYY-MM-DD`.
- **`tolerancia_min`** por defecto 5, configurable a nivel de sistema (RF-12).
- **Soft delete** en clientes y peluqueros (campo `activo`).
- **`estado` turno** como `TEXT` con check constraint: `pendiente|confirmado|en_curso|completado|cancelado`.

---

## 5. API REST — Contrato de endpoints

### 5.1 Autenticación
| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login, retorna JWT |
| POST | `/auth/register` | Crear usuario admin (solo si no existe ninguno) |

### 5.2 Peluqueros
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/peluqueros` | Listar peluqueros activos |
| POST | `/peluqueros` | Crear peluquero |
| GET | `/peluqueros/{id}` | Obtener peluquero + horarios |
| PUT | `/peluqueros/{id}` | Actualizar peluquero |
| DELETE | `/peluqueros/{id}` | Baja lógica |
| PUT | `/peluqueros/{id}/horarios` | Definir horarios semanales |
| POST | `/peluqueros/{id}/ausencias` | Marcar ausencia |

### 5.3 Servicios
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/servicios` | Listar servicios |
| POST | `/servicios` | Crear servicio |
| PUT | `/servicios/{id}` | Actualizar servicio |
| DELETE | `/servicios/{id}` | Baja lógica |

### 5.4 Clientes
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/clientes` | Listar clientes (búsqueda por query param) |
| POST | `/clientes` | Crear cliente |
| GET | `/clientes/{id}` | Obtener cliente + historial |
| PUT | `/clientes/{id}` | Actualizar cliente |
| DELETE | `/clientes/{id}` | Baja lógica |

### 5.5 Turnos (core)
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/turnos` | Listar turnos (filtros: fecha, cliente, peluquero) |
| POST | `/turnos` | Crear turno (valida solapamiento) |
| GET | `/turnos/{id}` | Obtener turno |
| PUT | `/turnos/{id}/estado` | Cambiar estado (transiciones válidas) |
| DELETE | `/turnos/{id}` | Cancelar turno (libera hueco) |

### 5.6 Agenda (vistas calculadas)
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/agenda/dia?fecha=YYYY-MM-DD` | Turnos del día por peluquero |
| GET | `/agenda/semana?fecha=YYYY-MM-DD` | Turnos de la semana |
| GET | `/agenda/disponibilidad?fecha=X&servicio_id=Y` | Huecos libres |

### 5.7 Dashboard y export
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/admin/dashboard` | Resumen del día |
| GET | `/export/dia?fecha=X&format=csv|pdf` | Exportar agenda del día |

---

## 6. Plan de implementación por fases

### Fase 1: Fundación (estructura + CRUD)
**Objetivo:** Proyecto Dockerizado, DB creada, endpoints CRUD básicos funcionando.

- [ ] Estructura de carpetas + Docker Compose
- [ ] SQLAlchemy models + inicialización DB
- [ ] Sistema de autenticación JWT
- [ ] CRUD completo: peluqueros, servicios, clientes
- [ ] Tests unitarios básicos

**Entrega:** API funcional con todos los CRUDs, probada con curl/httpie.

---

### Fase 2: Agenda y turnos (núcleo de negocio)
**Objetivo:** Crear/cancelar turnos con validación de solapamiento, vista agenda.

- [ ] TurnoService con validación de solapamiento (tolerancia incluida)
- [ ] Endpoints de turnos (POST, DELETE, cambio de estado)
- [ ] Cálculo de huecos disponibles (agenda_service)
- [ ] Endpoints de agenda (día, semana, disponibilidad)
- [ ] Frontend: vista de agenda día/semana (HTML/JS)
- [ ] Frontend: formulario crear turno con validación en tiempo real
- [ ] Tests de solapamiento y edge cases

**Entrega:** Se puede agendar un turno completo desde la web sin solapamientos.

---

### Fase 3: Recordatorios y notificaciones
**Objetivo:** Push local 24h antes del turno.

- [ ] APScheduler integrado en startup de FastAPI
- [ ] RecordatorioService: verificar turnos próximos cada 60s
- [ ] Service Worker + Notification API en frontend
- [ ] Historial de recordatorios en DB
- [ ] Configuración de anticipación (12h, 24h, 48h)

**Entrega:** Notificación push local al cumplirse el plazo configurado.

---

### Fase 4: Panel administrativo y export
**Objetivo:** Dashboard del día, búsqueda avanzada, exportar.

- [ ] Endpoint dashboard (turnos hoy, próximo turno, peluqueros activos)
- [ ] Búsqueda combinable (fecha + cliente + peluquero)
- [ ] Export CSV y PDF de la agenda del día
- [ ] Frontend: panel admin completo
- [ ] Roles: diferenciar admin vs recepcionista

**Entrega:** Panel administrativo funcional con export incluido.

---

### Fase 5: Hardening y documentación
**Objetivo:** Backup automáticos, tests de carga, DoD completo.

- [ ] BackupService: .backup diario a las 03:00
- [ ] Test manual completo: flujo feliz + 3 casos borde
- [ ] Lighthouse audit (< 3s carga inicial)
- [ ] Prueba offline (router apagado)
- [ ] README con instrucciones de despliegue
- [ ] DoD checklist completado

**Entrega:** Sistema listo para producción local en la peluquería.

---

## 7. Decisiones técnicas (registro ADR)

### ADR-001: FastAPI sobre Flask
**Contexto:** El documento de requerimientos sugiere "FastAPI/Flask".
**Decisión:** FastAPI.
**Razones:** Async nativo, validación automática con Pydantic, documentación OpenAPI automática, mejor rendimiento con Uvicorn.
**Consecuencia:** Ninguna negativa para este proyecto.

### ADR-002: SQLite sin ORM de abstracción extra
**Contexto:** Necesidad de archivo local, backup trivial.
**Decisión:** SQLite + SQLAlchemy (no Prisma, no Tortoise).
**Razones:** SQLAlchemy es el estándar de facto en Python, no agrega dependencias cloud, Alembic para migraciones si se necesitan.
**Consecuencia:** Si mañana necesitamos Postgres, el cambio es posible a nivel de connection string + migraciones.

### ADR-003: Frontend vanilla (sin framework)
**Contexto:** RN-02 exige carga < 3s, RN-04 responsive.
**Decisión:** HTML + JS vanilla + CSS.
**Razones:** Sin build step, sin node_modules, sin bundler. El proyecto es pequeño (SPA ligera). React/Vue agregan complejidad innecesaria.
**Consecuencia:** Si la UI crece mucho, reevaluar a un framework ligero (Preact, Alpine.js).

### ADR-004: Service Worker para notificaciones push
**Contexto:** RN-01 prohíbe nube. Web Push API requiere servidor (VAPID).
**Decución:** Notification API local desde Service Worker.
**Razones:** Las notificaciones se disparan desde el scheduler del backend, pero se muestran vía Notification API en el navegador cuando la pestaña está abierta. No requiere internet.
**Consecuencia:** Si la pestaña está cerrada, la notificación no llega. Para cobertura completa, se podría agregar un pequeño cliente de escritorio (opcional).

### ADR-005: JWT sin refresh token
**Contexto:** Sistema local, máximo 2 usuarios concurrentes.
**Decisión:** JWT simple con expiración de 8h (jornada laboral).
**Razones:** Sin refresh token simplifica la implementación. Si expira, se reloguea. No hay riesgo de seguridad significativo en entorno local.
**Consecuencia:** Usuario debe volver a loguear si pasa 8h (aceptable).

---

## 8. Infraestructura

### 8.1 Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8080:8000"
    volumes:
      - ./data:/app/data        # SQLite persistente
      - ./backups:/app/backups  # Backups automáticos
    environment:
      - DATABASE_URL=sqlite:///./data/turnos.db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-clave-local-cambiar-en-produccion}
      - TZ=America/Argentina/Buenos_Aires
    restart: unless-stopped
```

### 8.2 Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.3 Puertos y acceso
- **App:** `http://localhost:8080` (mapeado al puerto 8000 del contenedor)
- **API docs (Swagger):** `http://localhost:8080/docs`
- **Base de datos:** archivo en `./data/turnos.db`

---

## 9. Cumplimiento de requerimientos

| Requerimiento | Cómo se cumple |
|---------------|----------------|
| RN-01 (100% local) | Sin dependencias cloud, Docker todo-en-uno |
| RN-02 (carga < 3s) | Frontend vanilla sin build, assets mínimos |
| RN-03 (SQLite) | SQLite con WAL, backup por copia de archivo |
| RN-04 (responsive) | CSS mobile-first, probado en 375px y 1280px |
| RN-05 (roles) | JWT con claim `rol`, decoradores de permisos |
| RN-06 (español AR) | Toda la UI en español, formato dd/mm/aaaa |
| RN-07 (2 usuarios) | SQLite WAL soporta 2 conexiones concurrentes |

---

## 10. Riesgos técnicos identificados

| Riesgo | Mitigación |
|--------|------------|
| Service Worker no funciona en HTTP (solo HTTPS/localhost) | Documentar acceso por `localhost` o configurar certificado autofirmado |
| SQLite corruption si el servidor se apaga bruscamente | WAL mode + backups diarios + script de verificación de integridad |
| Recordatorio falla si el navegador está cerrado | Feature opcional: cliente de escritorio con Electron (fuera de alcance v1) |
| Escalabilidad > 3 peluqueros | SQLAlchemy permite migrar a Postgres cambiando connection string |

---

## 11. Próximos pasos (post-arquitectura)

1. **Validar arquitectura** con el equipo (Valen/PM + QA).
2. **Crear mockups/wireframes** de la vista de agenda y panel admin.
3. **Descomponer Fase 1** en tareas de desarrollo atómicas.
4. **Inicializar repositorio** con la estructura Docker base.

---

**Fin del documento de arquitectura.**
