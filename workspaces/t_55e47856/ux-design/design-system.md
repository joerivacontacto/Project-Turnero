# Design System: Calendario de Turnos — Peluquería

**Versión:** 1.0
**Fecha:** 2026-09-01
**Autor:** Sofia (UX)

---

## 1. Filosofía de diseño

El sistema está diseñado para dos perfiles con diferentes necesidades:

- **Peluqueros/administradores**: necesitan ver el panorama completo del día, detectar huecos rápidamente y gestionar turnos con mínima fricción. Usan la app desde desktop en la peluquería.
- **Clientes**: necesitan reservar en 30 segundos desde el móvil sin errores. El formulario debe ser ultra-simple.

**Principios guía:**
1. Cero aprendizaje: iconos + texto siempre juntos.
2. Feedback inmediato: cada acción tiene confirmación visual.
3. Prevención de errores: más que validar, evitar que ocurran.
4. Accesibilidad mínima: contraste AA, touch targets ≥ 44px.
5. Sin internet como feature: diseño que no depende de spinner de carga.

---

## 2. Paleta de colores

### Primarios
| Nombre | Hex | Uso |
|--------|-----|-----|
| Negro carbón | #1A1A2E | Texto principal, navbar |
| Blanco | #FFFFFF | Fondos, tarjetas |
| Crema cálida | #FAF7F2 | Fondo de pantalla (reduce fatiga visual) |

### Acentos
| Nombre | Hex | Uso |
|--------|-----|-----|
| Verde confirmación | #4CAF50 | Turnos confirmados, éxito |
| Azil info | #2196F3 | Turnos pendientes, enlaces |
| Naranja advertencia | #FF9800 | Turnos en curso |
| Rojo error | #F44336 | Cancelados, errores, validaciones |
| Gris neutro | #607D8B | Desactivados, placeholders |

### Semánticos de estado de turno
| Estado | Color | Ícono |
|--------|-------|-------|
| Pendiente | Azil #2196F3 | ⏳ |
| Confirmado | Verde #4CAF50 | ✓ |
| En curso | Naranja #FF9800 | ▶ |
| Completado | Gris oscuro #455A64 | ✓✓ |
| Cancelado | Rojo #F44336 | ✕ |

---

## 3. Tipografía

**Fuente:** Inter (o sans-serif del sistema: -apple-system, Segoe UI, Roboto)

| Elemento | Tamaño | Peso | Uso |
|----------|--------|------|-----|
| H1 | 24px | 700 | Título de pantalla |
| H2 | 18px | 600 | Subtítulos, nombres de peluquero |
| Body | 14px | 400 | Texto general |
| Caption | 12px | 400 | Horas, etiquetas pequeñas |
| Botón | 14px | 600 | CTAs |

---

## 4. Sistema de espaciado

Basado en grid de 4px:
- 4px: entre icono y texto
- 8px: entre elementos relacionados
- 16px: padding interno de tarjetas
- 24px: entre tarjetas / secciones
- 32px: separación de bloques grandes

---

## 5. Componentes reutilizables

### 5.1 TurnoCard (vista agenda)
```
┌─────────────────────────────┐
│ 09:00  María López          │  ← hora + nombre cliente
│        Corte · Juana (P)     │  · = separador
│ [✓ Confirmar] [✕ Cancelar] │  ← acciones rápidas (solo admin)
└─────────────────────────────┘
```
- Borde izquierdo de 4px con color de estado.
- Hover: eleva 2px, sombra suave.
- Touch target mínimo 44px de alto.

### 5.2 TimeSlot (hueco disponible)
```
┌──────────┐
│ 10:30    │
│ libre    │
│ [+ Nuevo]│
└──────────┘
```
- Fondo blanco con borde punteado gris.
- Solo visible en vista administrativa.

### 5.3 ServiceChip
```
┌───────────────┐
│ ✂ Corte  30m  │
└───────────────┘
```
- Chip redondeado (border-radius: 16px).
- Borde sólido, sin relleno.
- Seleccionado: relleno con color de acento.

### 5.4 Button (variantes)
- **Primary**: fondo carbón #1A1A2E, texto blanco, border-radius 8px.
- **Success**: fondo verde #4CAF50.
- **Danger**: fondo rojo #F44336.
- **Ghost**: sin fondo, borde gris.
- **Disabled**: opacidad 0.4, cursor not-allowed.

### 5.5 Modal / Dialog
- Overlay semitransparente negro 50%.
- Centrado, max-width 480px.
- Botón cerrar (✕) arriba a la derecha.
- Cerrar con Escape y click fuera.

### 5.6 Input
- Border 1px #CCC, border-radius 6px.
- Focus: border azul #2196F3, outline 2px azul 20%.
- Error: border rojo + mensaje debajo.

### 5.7 Toast / Notificación
- Posición: top-right.
- Auto-cierre 4s (dismissible manualmente).
- Colores según tipo: success, error, info, warning.

---

## 6. Layout base

### Desktop (≥1024px)
```
┌─────────────────────────────────────────────────────┐
│  NAVBAR: logo · Agenda · Clientes · Admin · [+Nuevo]│
├──────────┬──────────────────────────────────────────┤
│ SIDEBAR  │  CONTENIDO PRINCIPAL                     │
│ - Hoy    │                                          │
│ - Semana │  (vista activa: día/semana/mes)          │
│ - Mes    │                                          │
│ - Admin  │                                          │
└──────────┴──────────────────────────────────────────┘
```

### Móvil (<768px)
```
┌─────────────────────────┐
│  NAVBAR (hamburguesa)   │
├─────────────────────────┤
│                         │
│   CONTENIDO PRINCIPAL   │
│   (scroll vertical)     │
│                         │
├─────────────────────────┤
│  BOTTOM BAR: Hoy·Semana·Admin │
└─────────────────────────┘
```

---

## 7. Iconografía

Usar set simple ( Feather icons / Heroicons, o emojis como fallback):

| Acción | Ícono |
|--------|-------|
| Agregar turno | + |
| Editar | ✎ |
| Eliminar / Cancelar | ✕ |
| Buscar | 🔍 |
| Exportar | ⬇ |
| Configuración | ⚙ |
| Atrás | ← |
| Siguiente (fecha) | → |
| Anterior (fecha) | ← |
| Calendario | 📅 |
| Usuario | 👤 |
| Servicio | ✂ |
| Confirmar | ✓ |
| Notificar | 🔔 |
| Filtrar | ⚡ |

---

## 8. Patrones de interacción

### 8.1 Crear turno (flujo óptimo)
1. Usuario hace click en hueco disponible (o botón "+ Nuevo Turno").
2. Se abre modal con formulario.
3. Paso 1: Seleccionar cliente (buscador con autocompletar).
4. Paso 2: Seleccionar servicio (chips).
5. Paso 3: Confirmar fecha/hora (pre-seleccionada).
6. Confirmar → toast "Turno creado" → modal cierra.

**Objetivo:** <30 segundos según DoD.

### 8.2 Cancelar turno
1. Click en turno → modal de detalle.
2. Botón "Cancelar turno" (rojo).
3. Confirmación: "¿Seguro que deseas cancelar el turno de María López?"
4. Confirmar → hueco se libera → toast "Turno cancelado".

### 8.3 Detectar solapamiento
- Al intentar crear un turno que se solapa, el input de hora muestra error en tiempo real.
- El hueco conflictual se muestra brevemente en rojo.
- Mensaje: "Este horario se superpone con el turno de María López (09:00-09:30)".

---

## 9. Criterios de usabilidad (heurísticas)

1. **Visibilidad del sistema**: siempre se ve el día actual, el peluquero activo y los estados de turnos.
2. **Coincidencia sistema-realidad**: lenguaje del peluquero ("corte", "coloración"), no técnico.
3. **Control y libertad**: deshacer cancelación (reactivar turno).
4. **Consistencia**: mismo componente de turno en todas las vistas.
5. **Prevención de errores**: horarios no disponibles aparecen grises, no seleccionables.
6. **Reconocimiento > recuerdo**: historial visible al buscar cliente.
7. **Flexibilidad**: atajos de teclado (N = nuevo turno, Esc = cerrar modal).
8. **Diseño estético y minimalista**: sin elementos decorativos innecesarios.
9. **Recuperación de errores**: mensajes en español coloquial, sin códigos.
10. **Ayuda**: tooltips en iconos, onboarding primer uso.

---

## 10. Accesibilidad mínima

- Contraste texto/fondo ≥ 4.5:1 (WCAG AA).
- No usar color como único indicador (siempre + texto/ícono).
- Labels en todos los inputs (no placeholder como label).
- Focus visible (outline azul).
- Keyboard navigation: Tab lógico, Enter activa, Escape cierra modales.
- Touch targets ≥ 44×44px.

