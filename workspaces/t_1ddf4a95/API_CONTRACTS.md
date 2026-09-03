# API Contratos — Calendario de Turnos

## Autenticación
| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login, retorna JWT |
| POST | `/auth/register` | Crear usuario admin (solo si no existe ninguno) |
| GET | `/auth/me` | Obtener usuario actual |

## Peluqueros
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/peluqueros` | Listar peluqueros activos |
| POST | `/peluqueros` | Crear peluquero |
| GET | `/peluqueros/{id}` | Obtener peluquero |
| PUT | `/peluqueros/{id}` | Actualizar peluquero |
| DELETE | `/peluqueros/{id}` | Baja lógica |
| PUT | `/peluqueros/{id}/horarios` | Definir horarios semanales |
| POST | `/peluqueros/{id}/ausencias` | Marcar ausencia |

## Servicios
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/servicios` | Listar servicios |
| POST | `/servicios` | Crear servicio |
| PUT | `/servicios/{id}` | Actualizar servicio |
| DELETE | `/servicios/{id}` | Baja lógica |

## Clientes
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/clientes` | Listar clientes (búsqueda por `?q=`) |
| POST | `/clientes` | Crear cliente |
| GET | `/clientes/{id}` | Obtener cliente |
| PUT | `/clientes/{id}` | Actualizar cliente |
| DELETE | `/clientes/{id}` | Baja lógica |

## Turnos (core)
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/turnos` | Listar turnos (filtros: `fecha`, `cliente_id`, `peluquero_id`) |
| POST | `/turnos` | Crear turno (valida solapamiento) |
| GET | `/turnos/{id}` | Obtener turno |
| PUT | `/turnos/{id}/estado` | Cambiar estado (transiciones válidas) |
| DELETE | `/turnos/{id}` | Cancelar turno |

### Transiciones de estado válidas
```
pendiente → confirmado, cancelado
confirmado → en_curso, cancelado
en_curso → completado, cancelado
completado → (final)
cancelado → (final)
```

### Validaciones de creación de turno
- Cliente, peluquero y servicio existen y están activos
- Peluquero ofrece el servicio
- Hora fin > hora inicio
- Dentro del horario laborable del día
- Peluquero no está ausente
- No hay solapamiento (con tolerancia en minutos)

## Agenda
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/agenda/dia?fecha=YYYY-MM-DD` | Turnos del día |
| GET | `/agenda/semana?fecha=YYYY-MM-DD` | Turnos de la semana |
| GET | `/agenda/disponibilidad?fecha=X&servicio_id=Y` | Huecos libres |

## Admin
| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/admin/dashboard` | Resumen del día |
| GET | `/admin/export/dia?fecha=X&format=csv` | Exportar agenda del día |

## Modelo de datos
- SQLite con WAL mode
- Horas como TEXT `HH:MM` (hora local Argentina)
- Fechas como TEXT `YYYY-MM-DD`
- Soft delete con campo `activo`
- Estados con CHECK constraint

## Ejemplos de uso

### Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# {"access_token":"...", "token_type":"bearer", "rol":"admin"}
```

### Crear turno
```bash
curl -X POST http://localhost:8001/turnos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id":1,"peluquero_id":1,"servicio_id":1,"fecha":"2026-09-02","hora_inicio":"10:00","hora_fin":"10:30"}'
```

### Listar disponibilidad
```bash
curl "http://localhost:8001/agenda/disponibilidad?fecha=2026-09-02&servicio_id=1" \
  -H "Authorization: Bearer $TOKEN"
```
