# Documento de Requerimientos: Calendario de Turnos — Peluquería

**Versión:** 1.0
**Fecha:** 2026-09-01
**Autor:** Valen (PM)
**Estado:** Borrador para validación

---

## 1. Resumen ejecutivo

Sistema de gestión de turnos para una peluquería. Debe permitir a los clientes reservar turnos online (web) y al personal administrar la agenda localmente. **Restricción no negociable:** todo corre en local (sin nube, sin servicios externos, sin APIs de terceros).

Alcance: peluquería de 1-3 peluqueros. No pensado para cadena ni múltiples sucursales en esta versión.

---

## 2. Alcope y exclusiones

### Dentro del alcance
- Tipos de turno: corte, coloración, peinado (configurables).
- Gestión de peluqueros (altas/bajas, horarios disponibles).
- Gestión de clientes (datos de contacto, historial básico).
- Agenda visual (día/semana).
- Recordatorios automáticos (push local o email si hay SMTP local).
- Bloqueo de huecos por solapamiento.
- Panel administrativo local.

### Fuera del alcance
- Pagos / facturación.
- App móvil nativa (responsive web basta).
- Multi-sucursal.
- Sincronización entre dispositivos vía nube.
- Integración con calendarios externos (Google Calendar, etc.).

---

## 3. Requerimientos funcionales

### 3.1 Gestión de peluqueros
| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RF-01 | Alta/baja/modificación de peluqueros | Un peluquero puede desactivarse sin perder historial |
| RF-02 | Definir servicios que presta cada peluquero | Un peluquero puede estar asignado a 1+ servicios |
| RF-03 | Definir horario laborable (días + franjas) | Bloquea turnos fuera de disponibilidad |
| RF-04 | Marcar días de vacaciones/ausencia | Esos días no aparecen como disponibles |

### 3.2 Catálogo de servicios (tipos de turno)
| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RF-05 | Crear servicio con nombre, duración y precio | Duración en minutos, configurable por servicio |
| RF-06 | Tipos iniciales: corte, coloración, peinado | Se pueden agregar más sin tocar código |
| RF-07 | Servicio puede requerir peluquero específico o cualquiera | Evita asignar un colorista para un corte |

### 3.3 Agenda y turnos
| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RF-08 | Vista de agenda: día y semana | Muestra turnos asignados por peluquero |
| RF-09 | Crear turno asignando cliente + servicio + peluquero + franja | No permite solapamientos (validación en tiempo real) |
| RF-10 | Cancelar / reagenerar turno | Libera el hueco automáticamente |
| RF-11 | Duración se calcula desde el servicio seleccionado | No editable manualmente (evita errores) |
| RF-12 | Tolerancia de 5 min entre turnos configurable | Buffer para limpieza/preparación |
| RF-13 | Estado del turno: pendiente, confirmado, en curso, completado, cancelado | Transiciones válidas: pendiente → confirmado → completado, cualquiera → cancelado |

### 3.4 Gestión de clientes
| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RF-14 | Alta de cliente: nombre, teléfono, email opcional | Búsqueda por nombre o teléfono al agendar |
| RF-15 | Historial de turnos del cliente | Lista cronológica con estado |
| RF-16 | Baja lógica de cliente | No aparece en búsquedas pero se conservan registros |

### 3.5 Recordatorios
| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RF-17 | Recordatorio 24h antes del turno | Push local en la web (Notification API) |
| RF-18 | Recordatorio configurable: 12h, 24h, 48h | Por defecto 24h, configurable por peluquería |
| RF-19 | Historial de recordatorios enviados | Log local con timestamp y estado |

### 3.6 Panel administrativo
| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RF-06a | Dashboard del día: turnos de hoy, próximo turno, peluqueros disponibles | Vista rápida sin navegación |
| RF-20 | Búsqueda de turnos por fecha / cliente / peluquero | Filtros combinables |
| RF-21 | Exportar agenda del día (PDF o CSV) | Botón directo |

---

## 4. Requerimientos no funcionales

| ID | Requerimiento | Criterio de aceptación |
|----|--------------|----------------------|
| RN-01 | **100% local** — sin dependencias cloud | La app corre apagando el router |
| RN-02 | Tiempo de carga inicial < 3s en red local | Medido en Chrome Lighthouse |
| RN-03 | Datos persistidos en SQLite (o similar, archivo local) | Backup = copiar archivo de BD |
| RN-04 | Responsive: funciona en móvil y desktop | Probado en viewport 375px y 1280px |
| RN-05 | Roles: administrador y recepcionista (solo lectura parcial) | Recepcionista no modifica catálogo de servicios |
| RN-06 | Interfaz en español (Argentina) | $ en pesos, formato dd/mm/aaaa |
| RN-07 | Soporta 2 usuarios concurrentes sin degradación | Test de carga manual |

---

## 5. Restricciones

1. **Sin internet requerido.** Todo funciona offline.
2. **Sin dependencias de nube:** sin Firebase, sin AWS, sin SaaS.
3. **Un solo servidor local** que atienda web + API.
4. **Stack sugerido (validar con bot-fede):** Python (FastAPI/Flask) + SQLite + HTML/JS vanilla.
5. **Presupuesto:** proyecto personal/peluquería choca. Sin licencias pagas.

---

## 6. Criterios de aceptación globales (Definition of Done)

- [ ] Se puede agendar un turno completo en < 30 segundos.
- [ ] No se pueden crear turnos solapados bajo ninguna circunstancia.
- [ ] El recordatorio se dispara a la hora configurada (error < 1 min).
- [ ] Se puede usar sin conexión a internet (router apagado).
- [ ] Los datos sobreviven a reinicio del servidor.
- [ ] Test manual completo: flujo feliz + 3 casos borde documentados.

---

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Pérdida de datos por fallo de disco | Script de backup automático del archivo SQLite (diario) |
| Horario de verano / cambios de huso | Usar siempre hora local del sistema, no UTC |
| Más de 3 peluqueros en el futuro | Arquitectura que permita escalar sin refactor |

---

## 8. Próximos pasos sugeridos

1. Validar este documento con el cliente (peluquero).
2. Consultar a bot-fede para definición técnica (stack, arquitectura).
3. Crear mockup/wireframe de la vista de agenda.
4. Descomponer en tareas de desarrollo.
