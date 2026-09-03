# 📋 Calendario de Turnos

Sistema de gestión de turnos para comercio — 100% local / sin nube.

- **Proyecto:** Calendario de Turnos
- **Alcance:** 100% Local / Sin nube
- **Agentes:** 9 participantes
- **Tareas:** 10 tareas kanban
- **Estado:** Correcciones aplicadas

## 🏗️ Arquitectura del Sistema

- **Cliente:** Agenda Web + Panel Admin + Service Worker
- **API:** FastAPI (Python)
- **Base de datos:** SQLite + WAL Mode (`turnos.db`)
- **Jobs:** APScheduler (recordatorios + backup automático)
- **Infra:** Docker Compose con volúmenes persistentes

Flujo: Navegador → HTTP/REST → FastAPI → SQLite + APScheduler → Docker/volúmenes.

## 👥 Participantes y Responsabilidades

- **Valen (PM):** Documento de requerimientos completo (21 RF, 7 RNF, DoD, MoSCoW).
- **Fede (Tech Lead):** Arquitectura del sistema (stack FastAPI + SQLAlchemy + SQLite + JS vanilla + Docker, 28 endpoints, 8 entidades, 5 ADRs).
- **Sofia (UX Designer):** Design system completo, wireframes navegables (5 vistas), 10 decisiones UX justificadas.
- **Jose (Backend Developer):** API REST con 20 endpoints, validaciones de negocio, JWT auth.
- **Cele (Frontend Developer):** SPA vanilla con calendario mensual/semanal, formulario 3 pasos, panel admin, modo demo offline.
- **Gaston (DevOps):** Docker Compose, Dockerfile, scripts start/stop/backup/reset, healthcheck, volúmenes persistentes.
- **Juli (QA Engineer):** Revisión estática exhaustiva; detectó 5 bugs críticos de integración frontend-backend.
- **Nico (Customer Success):** Validación con cliente real (15/15 pruebas API exitosas); confirmó bugs del frontend.
- **Herminio (Director / Orquestador):** Aplicó los 5 fixes críticos en frontend y sincronizó contratos API.

## ⏱️ Línea de Tiempo

- **2026-09-01 15:28** — Valen: Documento de Requerimientos
- **2026-09-01 15:31** — Fede: Arquitectura del Sistema
- **2026-09-01 15:31** — Sofia: Diseño UX
- **2026-09-01 15:35** — Gaston: Infraestructura Docker
- **2026-09-01 15:40** — Jose: Backend API
- **2026-09-01 15:54** — Cele: Frontend SPA
- **2026-09-01 16:16** — Juli: QA — Revisión Estática
- **2026-09-01 16:26** — Nico: Validación con Cliente Real
- **2026-09-02 21:11** — Herminio: Aplicación de Correcciones

## ✅ Correcciones Aplicadas

1. **Bug 1 — `hora_fin` faltante en creación de turno:** `crearTurno()` calcula y envía `hora_fin` a partir de `hora_inicio` + duración del servicio.
2. **Bug 2 — `peluquero_id` nulo al elegir "Cualquiera":** Ahora asigna el primer peluquero disponible cuando no se elige uno específico.
3. **Bug 3 — Query param de búsqueda de clientes incorrecto:** Cambiado de `?busqueda=` a `?q=` para coincidir con el backend.
4. **Bug 4 — Parser de disponibilidad incorrecto:** Ahora maneja correctamente la respuesta del backend (`Array.isArray(data) ? ... : (data.horarios || [])`).
5. **Bug 5 — Ruta de export CSV incorrecta:** Corregida de `/export/dia` a `/admin/export/dia`.

## 📊 Diagrama de Flujo de Trabajo

- Requerimientos → Arquitectura → Diseño UX → DevOps/Docker
- Backend API → Frontend SPA → QA → Validación Cliente
- Backend Funcional consolidado; pendiente verificación E2E con Docker

## 📝 Entregables por Agente

- **Valen (PM):** `requerimientos-calendario-turnos.md`
- **Fede (Tech Lead):** `arquitectura-calendario-turnos.md`
- **Sofia (UX):** `design-system.md`, `wireframes.html`, `ux-decisions.md`
- **Jose (Backend):** `app/main.py`, `app/routes/`, `app/services/`, `app/database.py`, `init_db.py`, `API_CONTRACTS.md`, `test_api.py`
- **Cele (Frontend):** `index.html`, `css/main.css`, `js/api.js`, `js/app.js`
- **Gaston (DevOps):** `docker-compose.yml`, `Dockerfile`, `start.sh`, `stop.sh`, `backup.sh`, `reset.sh`, `logs.sh`, `README.md`
- **Juli (QA):** Revisión estática con 5 bugs críticos identificados
- **Nico (Customer Success):** `validation_report.md`, `test_client_flow.py`, `test_frontend_bugs.py`
- **Herminio (Director):** Aplicó los 5 fixes frontend y sincronizó contratos API

## 🔍 Hallazgos Clave

- ✅ Backend sólido: API funcional con 20 endpoints y validaciones completas.
- ✅ Frontend actualizado: corregidos los 5 bugs críticos de integración.
- 🏗️ Arquitectura bien diseñada: stack apropiado y separación de capas.
- 🔒 Seguridad implementada: JWT, hash de passwords, protección por rol.
- 🐳 DevOps completo: Docker con volúmenes persistentes, healthcheck y scripts.

## 📌 Próximos Pasos Recomendados

1. Verificación E2E completa levantando el stack con Docker.
2. Sincronización final de contratos: confirmar nombres de campos y endpoints entre frontend y backend.
3. Pruebas de aceptación con usuario real para validar flujos de reserva, edición y cancelación.
