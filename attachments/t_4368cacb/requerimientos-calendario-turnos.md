# REQUERIMIENTOS: Sistema de Calendario de Turnos para Peluquería

**Versión:** 1.0
**Fecha:** 2026-09-01
**Autor:** Valen (PM)
**Ambito:** Sistema LOCAL, sin deploy en nube.

---

## 1. OBJETIVO

Desarrollar un sistema local de gestión de turnos para una peluquería que permita agendar, visualizar y administrar reservas de servicios, asignación de peluqueros, gestión de clientes y envío de recordatorios. Todo el sistema corre en máquina local del negocio, sin dependencias de servicios cloud.

---

## 2. ALCANCE INCLUIDO (IN)

- Calendario visual de turnos (vista diaria/semanal/mensual).
- Tipos de turnos: corte, coloración, peinado (y combinaciones).
- Definición de duración por tipo de servicio.
- Asignación de peluqueros a turnos.
- Gestión de clientes (alta, baja, modificación, historial).
- Recordatorios automáticos (por email/SMS/WhatsApp — configurable).
- Bloqueos de horarios (almuerzos, feriados, licencias).
- Interfaz usable desde computadora de escritorio (no mobile-first, pero responsiva básica).
- Persistencia local (base de datos archivo único, sin servidor externo).

---

## 3. ALCANCE EXCLUIDO (OUT)

- Deploy en nube / hosting externo.
- Aplicación móvil nativa.
- Integración con pasarelas de pago.
- Facturación electrónica / AFIP.
- Acceso remoto desde internet.
- Multi-sucursal.
- App para clientes (solo panel administrativo del negocio).

---

## 4. ACTORES

| Actor | Rol |
|-------|-----|
| Encargado/admin | Gestiona el sistema completo, crea usuarios, configura servicios |
| Peluquero/a | Consulta su agenda, marca asistencia, ve historial propio |
| Cliente (indirecto) | Recibe confirmaciones y recordatorios (no interactúa con el sistema directamente) |

---

## 5. REQUERIMIENTOS FUNCIONALES

### 5.1 Gestión de Servicios y Duraciones

- **RF-001:** El sistema debe permitir definir tipos de servicio con nombre, duración en minutos y precio de referencia.
- **RF-002:** Servicios base obligatorios: Corte, Coloración, Peinado.
- **RF-003:** Un turno puede combinar múltiples servicios (ej: corte + coloración). La duración del turno = suma de duraciones de servicios seleccionados + buffer configurable (default 10 min).
- **RF-004:** Duraciones por defecto: Corte = 30 min, Coloración = 60 min, Peinado = 45 min. Editables por el admin.

### 5.2 Calendario y Turnos

- **RF-005:** Vista de calendario con granularidad diaria y semanal (mínimo).
- **RF-006:** Crear turno: seleccionar cliente, servicio(s), peluquero, fecha, hora.
- **RF-007:** El sistema NO debe permitir solapamiento de turnos para un mismo peluquero.
- **RF-008:** El sistema debe validar horario de atención (ej: Lun-Sáb 9:00-20:00, configurable).
- **RF-009:** Cancelar turno con motivo (obligatorio) y registro de quién canceló.
- **RF-010:** Marcar turno como "asistió" / "no asistió" / "cancelado por cliente".

### 5.3 Asignación de Peluqueros

- **RF-011:** Cada turno tiene exactamente un peluquero asignado.
- **RF-012:** El sistema debe mostrar la agenda individual de cada peluquero.
- **RF-013:** Bloqueos por peluquero: vacaciones, licencias, feriados personales.
- **RF-014:** Reasignación de turno a otro peluquero (arrastrar o editar).

### 5.4 Gestión de Clientes

- **RF-015:** Alta de cliente: nombre, teléfono (obligatorio), email (opcional), notas.
- **RF-016:** Búsqueda rápida por nombre o teléfono.
- **RF-017:** Historial de turnos por cliente (últimos 12 meses visible, resto accesible).
- **RF-018:** Datos del cliente editables; baja lógica (no se borra, se marca inactivo).

### 5.5 Recordatorios

- **RF-019:** Recordatorio automático configurable (ej: 24h antes del turno).
- **RF-020:** Canal configurable: email, SMS o WhatsApp (vía gateway local si aplica).
- **RF-021:** El sistema debe registrar cada recordatorio enviado (timestamp + canal + estado).
- **RF-022:** Confirmación de asistencia por parte del cliente (si el canal lo permite).

### 5.6 Usuarios y Permisos

- **RF-023:** Login local (usuario + contraseña). Sin OAuth, sin login social.
- **RF-024:** Roles: Admin (acceso total), Peluquero (solo su agenda).
- **RF-025:** El admin puede crear/editar/borrar usuarios.

### 5.7 Reportes

- **RF-026:** Resumen diario de turnos (cantidad, asistencias, cancelaciones).
- **RF-027:** Exportar agenda del día a PDF (para imprimir o guardar).
- **RF-028:** Reporte mensual de facturación estimada (turnos realizados × precio servicio).

---

## 6. REQUERIMIENTOS NO FUNCIONALES

### 6.1 Tecnología y Plataforma

- **RNF-001:** Aplicación desktop o web local. Preferencia: web local (navegador) para no instalar binarios.
- **RNF-002:** Backend: Python (Flask/FastAPI) o Node.js (Express). Eligible por implementador.
- **RNF-003:** Frontend: HTML + CSS + JS vanilla o framework ligero (sin build step pesado). Mínimo: HTML/CSS/JS directo.
- **RNF-004:** Base de datos: SQLite (archivo local, sin servidor).
- **RNF-005:** Toda la aplicación corre en localhost. Sin dependencias externas en runtime.

### 6.2 Rendimiento

- **RNF-006:** Carga inicial del calendario < 2 segundos con hasta 1000 turnos en la BD.
- **RNF-007:** Creación/edición de turno responde < 500ms.

### 6.3 Seguridad (local)

- **RNF-008:** Contraseñas hasheadas (bcrypt o argon2).
- **RNF-009:** Sin exposición a internet. Solo accesible en red local o localhost.
- **RNF-010:** Logs de acciones críticas (crear/cancelar turno, modificar cliente) con timestamp y usuario.

### 6.4 Usabilidad

- **RNF-011:** Interfaz en español.
- **RNF-012:** Flujo de creación de turno en ≤ 3 clics desde calendario.
- **RNF-013:** Accesible desde Chrome / Firefox / Edge (últimas 2 versiones).

### 6.5 Mantenibilidad

- **RNF-014:** Código documentado (README con setup, run, tests).
- **RNF-015:** Sin vendor lock: dependencias mínimas, preferencia por stdlib.

---

## 7. CRITERIOS DE ACEPTACIÓN (Definición de Listo)

| # | Criterio |
|---|----------|
| AC-001 | Se puede crear un turno con cliente, peluquero y servicio en menos de 30 segundos. |
| AC-002 | El sistema impide solapamiento de turnos para un mismo peluquero (test automático). |
| AC-003 | Un cliente con 10 turnos en el historial se puede buscar en < 1 segundo. |
| AC-004 | La agenda semanal muestra todos los turnos sin errores de render (test visual). |
| AC-005 | Los recordatorios se envían en el horario configurado (test con reloj simulado o log). |
| AC-006 | Un usuario con rol "Peluquero" NO puede ver la agenda de otro peluquero. |
| AC-007 | La aplicación arranca en localhost con un comando (ej: `python app.py` o `npm start`). |
| AC-008 | La base de datos se genera automáticamente en primer run (migración/init automático). |
| AC-009 | Hay al menos 1 test funcional por cada RF crítico (RF-006, RF-007, RF-015, RF-019). |

---

## 8. RESTRICCIONES Y SUPUESTOS

- **RES-001:** El negocio tiene una sola ubicación (mono-sucursal).
- **RES-002:** El hardware disponible es una PC de escritorio/laptop con 4GB RAM mínimo.
- **RES-003:** Sistema operativo: Windows 10/11 o Linux (Mint/Ubuntu).
- **RES-004:** No hay conexión a internet garantizada; el sistema funciona offline.
- **RES-005:** Los recordatorios por email/SMS requieren que la PC tenga acceso a internet en el momento del envío, pero el resto del sistema no.

---

## 9. PRIORIZACIÓN (MoSCoW)

| Prioridad | Requerimientos |
|-----------|----------------|
| **Must have** | RF-001 a RF-012 (servicios, turnos, calendario, peluqueros), RF-015 a RF-018 (clientes), RF-023 a RF-025 (login), RF-006 a RF-008 (NFunc base) |
| **Should have** | RF-013, RF-014 (bloqueos/reasignación), RF-019 a RF-022 (recordatorios), RF-026 a RF-028 (reportes), RF-009 (logs) |
| **Could have** | Confirmación de asistencia del cliente (RF-022), export PDF (RF-027), reporte facturación (RF-028) |
| **Won't have (v1)** | Pagos, facturación, app móvil, multi-sucursal, acceso remoto |

---

## 10. ENTREGABLES ESPERADOS

1. Documento de requerimientos (este documento) — ✅ entregado.
2. Prototipo de baja fidelidad (wireframe HTML estático) — pendiente.
3. Estructura de base de datos (esquema SQL) — pendiente.
4. API endpoints definidos (OpenAPI/Swagger o lista simple) — pendiente.
5. Setup script (instrucciones para levantar el sistema en localhost) — pendiente.
6. Tests funcionales mínimos — pendiente.

---

## 11. GLOSARIO

| Término | Definición |
|---------|------------|
| Turno | Reserva de un servicio para un cliente en un horario específico con un peluquero asignado |
| Servicio | Tipo de trabajo ofrecido (corte, coloración, peinado) con duración y precio |
| Buffer | Tiempo muerto entre turnos para limpieza y preparación |
| Baja lógica | Registro marcado como inactivo pero conservado en base de datos |
