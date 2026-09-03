from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from app.schemas import TurnoCreate, TurnoUpdateEstado
from app.utils.time import ahora_str, hoy_str, time_to_minutes, add_minutes
from app.config import get_settings

settings = get_settings()

TRANSICIONES_VALIDAS = {
    "pendiente": ["confirmado", "cancelado"],
    "confirmado": ["en_curso", "cancelado"],
    "en_curso": ["completado", "cancelado"],
    "completado": [],
    "cancelado": [],
}

class TurnoService:
    def __init__(self, db):
        self.db = db

    def crear_turno(self, data: TurnoCreate) -> Tuple[Optional[dict], Optional[str]]:
        # Validar que existan las entidades
        cliente = self.db.execute(
            "SELECT * FROM clientes WHERE id = ? AND activo = 1", (data.cliente_id,)
        ).fetchone()
        if not cliente:
            return None, "Cliente no encontrado o inactivo"

        peluquero = self.db.execute(
            "SELECT * FROM peluqueros WHERE id = ? AND activo = 1", (data.peluquero_id,)
        ).fetchone()
        if not peluquero:
            return None, "Peluquero no encontrado o inactivo"

        servicio = self.db.execute(
            "SELECT * FROM servicios WHERE id = ? AND activo = 1", (data.servicio_id,)
        ).fetchone()
        if not servicio:
            return None, "Servicio no encontrado o inactivo"

        # Validar formato de horas
        inicio = time_to_minutes(data.hora_inicio)
        fin = time_to_minutes(data.hora_fin)
        if fin <= inicio:
            return None, "La hora de fin debe ser posterior a la hora de inicio"

        # Validar que el peluquero ofrezca el servicio
        peluquero_servicio = self.db.execute(
            "SELECT * FROM peluqueros_servicios WHERE peluquero_id = ? AND servicio_id = ?",
            (data.peluquero_id, data.servicio_id),
        ).fetchone()
        if not peluquero_servicio:
            return None, "El peluquero no ofrece este servicio"

        # Validar horario laborable
        dia_semana = datetime.strptime(data.fecha, "%Y-%m-%d").weekday()
        horario = self.db.execute(
            "SELECT * FROM horarios WHERE peluquero_id = ? AND dia_semana = ?",
            (data.peluquero_id, dia_semana),
        ).fetchone()
        if not horario:
            return None, "El peluquero no trabaja ese día"

        h_inicio = time_to_minutes(horario["hora_inicio"])
        h_fin = time_to_minutes(horario["hora_fin"])
        if inicio < h_inicio or fin > h_fin:
            return None, f"El turno está fuera del horario laborable ({horario['hora_inicio']}-{horario['hora_fin']})"

        # Validar ausencia
        ausencia = self.db.execute(
            "SELECT * FROM ausencias WHERE peluquero_id = ? AND fecha_inicio <= ? AND fecha_fin >= ?",
            (data.peluquero_id, data.fecha, data.fecha),
        ).fetchone()
        if ausencia:
            motivo = ausencia["motivo"] or "Sin motivo"
            return None, f"Peluquero ausente: {motivo}"

        # Validar solapamiento (con tolerancia)
        if self._hay_solapamiento(data.peluquero_id, data.fecha, data.hora_inicio, data.hora_fin, data.tolerancia_min):
            return None, "El turno se solapa con otro existente"

        cursor = self.db.execute(
            """INSERT INTO turnos (cliente_id, peluquero_id, servicio_id, fecha, hora_inicio, hora_fin, estado, tolerancia_min, creado_en)
               VALUES (?, ?, ?, ?, ?, ?, 'pendiente', ?, ?)""",
            (data.cliente_id, data.peluquero_id, data.servicio_id, data.fecha, data.hora_inicio, data.hora_fin, data.tolerancia_min, ahora_str()),
        )
        self.db.commit()
        turno_id = cursor.lastrowid
        return self.obtener_turno(turno_id), None

    def _hay_solapamiento(self, peluquero_id: int, fecha: str, hora_inicio: str, hora_fin: str, tolerancia: int, exclude_id: int = None) -> bool:
        inicio_nuevo = time_to_minutes(hora_inicio) - tolerancia
        fin_nuevo = time_to_minutes(hora_fin) + tolerancia

        query = "SELECT * FROM turnos WHERE peluquero_id = ? AND fecha = ? AND estado != 'cancelado'"
        params = [peluquero_id, fecha]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)

        for row in self.db.execute(query, params).fetchall():
            inicio_existente = time_to_minutes(row["hora_inicio"]) - row["tolerancia_min"]
            fin_existente = time_to_minutes(row["hora_fin"]) + row["tolerancia_min"]
            if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
                return True
        return False

    def cambiar_estado(self, turno_id: int, data: TurnoUpdateEstado) -> Tuple[Optional[dict], Optional[str]]:
        turno = self.db.execute("SELECT * FROM turnos WHERE id = ?", (turno_id,)).fetchone()
        if not turno:
            return None, "Turno no encontrado"

        estado_actual = turno["estado"]
        nuevo_estado = data.estado

        if nuevo_estado not in TRANSICIONES_VALIDAS.get(estado_actual, []):
            permitidos = TRANSICIONES_VALIDAS.get(estado_actual, [])
            return None, f"Transición inválida: {estado_actual} -> {nuevo_estado}. Permitidos: {permitidos}"

        self.db.execute("UPDATE turnos SET estado = ? WHERE id = ?", (nuevo_estado, turno_id))
        self.db.commit()
        return self.obtener_turno(turno_id), None

    def cancelar_turno(self, turno_id: int) -> Tuple[bool, Optional[str]]:
        turno = self.db.execute("SELECT * FROM turnos WHERE id = ?", (turno_id,)).fetchone()
        if not turno:
            return False, "Turno no encontrado"
        if turno["estado"] in ["completado", "cancelado"]:
            return False, f"No se puede cancelar un turno {turno['estado']}"
        self.db.execute("UPDATE turnos SET estado = 'cancelado' WHERE id = ?", (turno_id,))
        self.db.commit()
        return True, None

    def listar_turnos(self, fecha: str = None, cliente_id: int = None, peluquero_id: int = None) -> List[dict]:
        query = "SELECT * FROM turnos WHERE 1=1"
        params = []
        if fecha:
            query += " AND fecha = ?"
            params.append(fecha)
        if cliente_id:
            query += " AND cliente_id = ?"
            params.append(cliente_id)
        if peluquero_id:
            query += " AND peluquero_id = ?"
            params.append(peluquero_id)
        query += " ORDER BY fecha, hora_inicio"
        return [dict(r) for r in self.db.execute(query, params).fetchall()]

    def obtener_turno(self, turno_id: int) -> Optional[dict]:
        row = self.db.execute("SELECT * FROM turnos WHERE id = ?", (turno_id,)).fetchone()
        return dict(row) if row else None
