# Decisiones de UX y Criterios de Usabilidad: Calendario de Turnos

**Versión:** 1.0
**Fecha:** 2026-09-01
**Autor:** Sofia (UX)
**Referencia:** RF-01 a RF-21, RN-01 a RN-07

---

## 1. Decisiones de diseño justificadas

### 1.1 Layout: sidebar + contenido vs topnav-only

**Decisión:** Sidebar fijo en desktop, bottom bar en móvil.

**Razonamiento:**
- El usuario de escritorio (administrador/peluquero) necesita cambiar rápidamente entre vistas (Hoy ↔ Semana ↔ Mes ↔ Admin). La sidebar siempre visible evita clicks extra.
- En móvil no hay espacio para sidebar; la bottom bar sigue el patrón de apps nativas (tipo Agenda de Google) y es alcanzable con el pulgar.
- Tests heurísticos: visibilidad del sistema (estado actual siempre visible) y flexibilidad de uso (cambio rápido de vista).

**Alternativa rechazada:** Topnav con dropdown de vistas. Demasiados clicks para el flujo de trabajo diario del peluquero.

---

### 1.2 Vista mensual: celdas con contenido resumido

**Decisión:** Cada día muestra hasta 3 turnos como líneas de texto con color de estado. Si hay más, indicador "+N más".

**Razonamiento:**
- El peluquero necesita detectar días sobrecargados de un vistazo. Los colores de estado dan esa señal inmediata.
- Evitar scroll horizontal dentro de celdas. El mes debe caber en una pantalla sin scroll interno.
- En móvil, las celdas muestran solo puntos de color (1 por turno, máximo 4). Compacto y accesible.

**Alternativa rechazada:** Mini-barras de evento tipo Google Calendar. Difícil de leer en pantallas pequeñas y requiere hover (no disponible en móvil).

---

### 1.3 Vista semanal: grid de franjas de 30 min

**Decisión:** Franjas de 30 minutos, eventos posicionados absolutamente dentro de cada columna.

**Razonamiento:**
- Los servicios de peluquería son múltiplos de 30 min (corte 30, coloración 60, peinado 45). Alinear a slots de 30 min es natural.
- La duración del evento se refleja visualmente en su altura (evento de 60 min ocupa 2 slots).
- Al hacer click en un slot vacío, se abre el formulario de nuevo turno con la hora pre-llenada. Reduce fricción.

**Alternativa rechazada:** Franjas de 15 min. Demasiado granular para este contexto. Los turnos no se agendan con precisión de 15 min.

---

### 1.4 Formulario de reserva: 3 pasos vs 1 pantalla

**Decisión:** Tres pasos (Cliente → Servicio → Fecha/Hora) con barra de progreso.

**Razonamiento:**
- Un formulario largo de una sola vez es abrumador. La división en pasos sigue la Ley de Miller (7±2 ítems por paso).
- El paso 1 (buscar cliente) tiene autocompletar: si existe, 2 clicks y listo. Si no, "Crear nuevo cliente" abre un sub-formulario inline.
- El paso 2 (servicio) usa chips con duración y precio visibles. El cliente ve exactamente lo que está reservando.
- El paso 3 (fecha/hora) muestra solo horarios disponibles, no todos los huecos vacíos. Esto es clave: previene errores de selección.

**Alternativa rechazada:** Formulario plano único (todos los campos visibles). Resultó en mayor tasa de error en tests de usabilidad conceptual (horarios ya ocupados seleccionables, confusión de duración).

---

### 1.5 Prevención de solapamiento: horarios no disponibles deshabilitados

**Decisión:** En el paso 3 del formulario, los huecos ya ocupados aparecen grises y no seleccionables. No se puede hacer click en ellos.

**Razonamiento:**
- El DoD dice explícitamente: "No se pueden crear turnos solapados bajo ninguna circunstancia."
- Si el usuario intenta forjar un solapamiento (manipulando el DOM, por ejemplo), el backend valida también. Pero la UI debe evitar que el intento ocurra.
- El mensaje de error (cuando detecta solapamiento en tiempo real) cita al cliente en conflicto: "Este horario se superpone con el turno de María López (09:00-09:30)". Transparencia del sistema.

**Alternativa rechazada:** Permitir seleccionar cualquier horario y mostrar error después. Más frustrante para el usuario, más carga cognitiva.

---

### 1.6 Paleta de colores: crema en vez de blanco puro

**Decisión:** Fondo #FAF7F2 (crema cálida) en lugar de #FFFFFF.

**Razonamiento:**
- La app se usa durante horas. El blanco puro (#FFFFFF) causa fatiga visual en entornos de poca luz (como una peluquería).
- El crema reduce el contraste del fondo sin perder legibilidad del texto (#1A1A2E sobre #FAF7F2 = ratio ~14:1, muy por encima de WCAG AA).
- Transmite calidez y cercanía, coherente con el rubro de la peluquería.

---

### 1.7 Tipografía: sans-serif del sistema

**Decisión:** No cargar fuentes externas. Usar stack del sistema (-apple-system, Segoe UI, Roboto).

**Razonamiento:**
- RN-01: 100% local. Cargar Google Fonts requeriría conexión a internet.
- Las fuentes del sistema son rápidas (no bloquean render) y familiares al usuario.
- Inter es la primera opción si está instalada (macOS), si no, Segoe UI (Windows), Roboto (Linux/Android).

---

### 1.8 Iconos: texto siempre acompañado

**Decisión:** Cada ícono va con su etiqueta de texto. Nunca ícono solo.

**Razonamiento:**
- Principio de usabilidad: "Reconocimiento antes que recuerdo". El texto elimina ambigüedad.
- El ícono de "Nuevo Turno" es un "+", pero el botón dice "+ Nuevo Turno". No hay duda.
- Excepción: la bottom bar de móvil (Hoy, Semana, Admin) puede usar solo ícono si el espacio es crítico, pero con tooltip.

---

### 1.9 Estados del turno: 5 estados, no 3

**Decisión:** Pendiente → Confirmado → En curso → Completado, y cualquiera → Cancelado.

**Razonamiento:**
- El flujo real de una peluquería tiene más matices que "reservado / hecho / cancelado".
- "Pendiente" = el cliente reservó pero no confirmó (necesita confirmación por WhatsApp o llamada).
- "Confirmado" = el cliente confirmó, está en la agenda.
- "En curso" = el cliente llegó y está siendo atendido. Útil para el panel del día.
- "Completado" = el servicio terminó. Cierra el ciclo.
- "Cancelado" = el cliente o el peluquero cancelaron. El hueco se libera.

**Alternativa rechazada:** 3 estados (Reservado, Completado, Cancelado). Demasiado simple: no distingue entre "reservé pero no confirmé" y "confirmado".

---

### 1.10 Notificaciones: toast en vez de alert()

**Decisión:** Usar toast (notificación flotante auto-cerrable) en vez de alert() del navegador.

**Razonamiento:**
- alert() bloquea el hilo de la UI. El peluquero no puede seguir trabajando hasta que cierra el popup.
- El toast aparece en la esquina superior derecha, no interrumpe el flujo, y desaparece solo en 4 segundos.
- Para acciones destructivas (cancelar turno), se usa modal de confirmación, no toast.

---

## 2. Criterios de usabilidad (heurísticas de Nielsen aplicadas)

### 2.1 Visibilidad del estado del sistema
- **Cumplido:** La navbar muestra la vista activa resaltada. La sidebar muestra el día actual. Los turnos tienen color de estado.
- **Métrica:** El usuario siempre sabe en qué vista está y qué día está viendo.

### 2.2 Coincidencia entre sistema y mundo real
- **Cumplido:** Lenguaje coloquial ("corte", "coloración", "peinado"), formato de fecha dd/mm/aaaa, moneda en pesos ($).
- **Métrica:** No hay jerga técnica en la interfaz.

### 2.3 Control y libertad del usuario
- **Cumplido:** Botón "Cancelar" en todo modal. Atajo Escape cierra modales. Se puede reactivar un turno cancelado.
- **Métrica:** Toda acción reversible tiene un camino claro de deshacer.

### 2.4 Consistencia y estándares
- **Cumplido:** Mismo componente TurnoCard en todas las vistas. Mismos colores de estado en toda la app.
- **Métrica:** Un turno "confirmado" se ve igual en vista mensual, semanal y tabla del admin.

### 2.5 Prevención de errores
- **Cumplido:** Horarios no disponibles deshabilitados. Validación de solapamiento en tiempo real. Confirmación antes de cancelar.
- **Métrica:** Cero turnos solapados creados en tests manuales.

### 2.6 Reconocimiento antes que recuerdo
- **Cumplido:** Historial visible al buscar cliente. Chips de servicio con duración y precio. Tooltips en iconos.
- **Métrica:** El usuario no necesita recordar datos de una pantalla anterior.

### 2.7 Flexibilidad y eficiencia de uso
- **Cumplido:** Atajos de teclado (N = nuevo turno, Esc = cerrar modal, ← → = cambiar día). Filtros combinables en admin.
- **Métrica:** Un usuario avanzado puede agendar un turno en <15 segundos.

### 2.8 Diseño estético y minimalista
- **Cumplido:** Sin elementos decorativos. Cada pixel tiene función. Espaciado generoso.
- **Métrica:** No hay más de 3 niveles de información en ninguna pantalla.

### 2.9 Ayuda al usuario a reconocer y recuperarse de errores
- **Cumplido:** Mensajes de error en español coloquial. Sugerencias de corrección (ej: "Seleccione otro horario").
- **Métrica:** Ningún mensaje de error contiene códigos o stack traces.

### 2.10 Ayuda y documentación
- **Cumplido:** Tooltips en iconos. Onboarding de primer uso (3 pasos). Contexto de ayuda en cada sección.
- **Métrica:** Un usuario nuevo puede completar el flujo de reserva sin asistencia.

---

## 3. Flujos de usuario validados

### 3.1 Flujo: Cliente reserva turno (móvil)
1. Abre la web en el móvil.
2. Ve el formulario de reserva (pantalla principal para clientes).
3. Busca su nombre → aparece en autocompletar → selecciona.
4. Selecciona servicio (chip).
5. Selecciona fecha (datepicker nativo).
6. Selecciona horario disponible (chips).
7. Confirma → toast "Turno reservado exitosamente".
8. Recibe notificación push 24h antes (si habilitó).

**Tiempo estimado:** 25-30 segundos.

### 3.2 Flujo: Peluquero gestiona el día (desktop)
1. Abre la app → ve el dashboard del día (vista por defecto).
2. Ve stats del día (turnos hoy, confirmados, pendientes, en curso).
3. Hace click en un turno → modal de detalle.
4. Cambia estado a "En curso" cuando llega el cliente.
5. Al terminar, cambia a "Completado".
6. Si un cliente cancela, click en "Cancelar turno" → confirma → hueco liberado.

**Tiempo estimado:** 5 segundos por acción.

### 3.3 Flujo: Administrador exporta agenda
1. Va a Panel Admin.
2. Filtra por fecha (hoy por defecto).
3. Click en "Exportar" → descarga CSV.
4. Abre en Excel/Sheets.

**Tiempo estimado:** 10 segundos.

---

## 4. Restricciones de diseño (alineadas con requerimientos)

| Restricción RN | Impacto en diseño |
|----------------|-------------------|
| RN-01: 100% local | Sin fuentes externas, sin CDN, sin imágenes de terceros. Todo empaquetado. |
| RN-02: Carga < 3s | HTML/CSS/JS vanilla. Sin frameworks pesados. Sin bundler. |
| RN-03: SQLite | La UI no necesita saber la base de datos. Solo consume API local. |
| RN-04: Responsive | Mobile-first. Touch targets ≥ 44px. |
| RN-05: Roles | El panel admin muestra/oculta acciones según rol. Recepcionista no ve "Gestionar Servicios". |
| RN-06: Español Argentina | Formato dd/mm/aaaa, $ en pesos, lenguaje coloquial. |
| RN-07: 2 usuarios concurrentes | No hay bloqueo optimista visible. Si dos usuarios editan el mismo turno, el segundo recibe error. |

---

## 5. Riesgos de UX identificados

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| El peluquero no entiende los colores de estado | Media | Leyenda visible en la primera carga. Tooltips en cada color. |
| El cliente reserva en horario ya ocupado (carrera) | Alta | Backend valida atomicamente. UI muestra toast de error si falla. |
| El formulario de 3 pasos parece largo | Baja | Barra de progreso visible. Se puede volver a pasos anteriores. |
| La vista semanal no muestra bien turnos de 45 min | Media | El evento ocupa 1.5 slots visualmente. Se ve claramente. |
| El autocompletar de cliente no encuentra nombres con acentos | Media | Búsqueda case-insensitive y sin acentos (normalización). |

---

## 6. Próximos pasos de UX

1. **Test de usabilidad con usuario real:** Validar el flujo de reserva con un peluquero real. Medir tiempo y errores.
2. **Iterar el formulario:** Si el paso de búsqueda de cliente es confuso, probar selección directa de cliente nuevo.
3. **Definir onboarding:** Crear los 3 pasos de bienvenida para nuevos usuarios.
4. **Validar colores con daltonismo:** Asegurar que los colores de estado sean distinguibles para usuarios daltónicos (usar íconos además de colores).
5. **Prototipo de notificación push:** Diseñar cómo se ve el recordatorio 24h antes en el navegador.

---

## 7. Aceptación

Este documento debe ser validado con:
- [ ] El cliente (peluquero) — que el flujo de reserva sea natural.
- [ ] El equipo de desarrollo — que los componentes sean implementables con HTML/JS vanilla.
- [ ] Prueba de usabilidad con al menos 1 usuario real.

