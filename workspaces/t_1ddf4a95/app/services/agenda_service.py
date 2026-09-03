from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Turno, Peluquero, Servicio, Horario, Ausencia
from app.utils.time import time_to_minutes, add_minutes, hoy_str

class AgendaService:
    def __init__(self, db: Session):
        self.db = db

    def get_agenda_dia(self, fecha: str, peluquero_id: int = None) -> List[Turno]:
        """Obtiene los turnos de un día, opcionalmente filtrados por peluquero."""
        query = self.db.query(Turno).filter(
            Turno.fecha == fecha,
            Turno.estado.notin_(["cancelado"]),
        )
        if peluquero_id:
            query = query.filter(Turno.peluquero_id == peluquero_id)
        return query.order_by(Turno.hora_inicio).all()

    def get_agenda_semana(self, fecha: str) -> List[dict]:
        """Obtiene los turnos de la semana que contiene la fecha dada."""
        dt = datetime.strptime(fecha, "%Y-%m-%d")
        inicio_semana = dt - timedelta(days=dt.weekday())
        fin_semana = inicio_semana + timedelta(days=6)

        turnos = self.db.query(Turno).filter(
            Turno.fecha >= inicio_semana.strftime("%Y-%m-%d"),
            Turno.fecha <= fin_semana.strftime("%Y-%m-%d"),
            Turno.estado.notin_(["cancelado"]),
        ).order_by(Turno.fecha, Turno.hora_inicio).all()

        # Agrupar por día
        dias = {}
        for turno in turnos:
            if turno.fecha not in dias:
                dias[turno.fecha] = []
            dias[turno.fecha].append(turno)

        resultado = []
        for i in range(7):
            dia = (inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d")
            resultado.append({
                "fecha": dia,
                "turnos": dias.get(dia, []),
            })
        return resultado

    def get_disponibilidad(self, fecha: str, servicio_id: int) -> List[dict]:
        """Calcula huecos disponibles para un servicio en una fecha."""
        servicio = self.db.query(Servicio).filter(Servicio.id == servicio_id, Servicio.activo == True).first()
        if not servicio:
            return []

        dt = datetime.strptime(fecha, "%Y-%m-%d")
        dia_semana = dt.weekday()

        peluqueros_con_servicio = self.db.query(Peluquero).join(
            PeluqueroServicio
        ).filter(
            PeluqueroServicio.servicio_id == servicio_id,
            Peluquero.activo == True,
        ).all()

        huecos = []
        for peluquero in peluqueros_con_servicio:
            horario = self.db.query(Horario).filter(
                Horario.peluquero_id == peluquero.id,
                Horario.dia_semana == dia_semana,
            ).first()
            if not horario:
                continue

            # Verificar ausencia
            ausencia = self.db.query(Ausencia).filter(
                Ausencia.peluquero_id == peluquero.id,
                Ausencia.fecha_inicio <= fecha,
                Ausencia.fecha_fin >= fecha,
            ).first()
            if ausencia:
                continue

            # Calcular huecos libres
            turnos_ocupados = self.db.query(Turno).filter(
                Turno.peluquero_id == peluquero.id,
                Turno.fecha == fecha,
                Turno.estado.notin_(["cancelado"]),
            ).order_by(Turno.hora_inicio).all()

            huecos_peluquero = self._calcular_huecos(
                horario.hora_inicio,
                horario.hora_fin,
                turnos_ocupados,
                servicio.duracion_min,
            )

            if huecos_peluquero:
                huecos.append({
                    "peluquero_id": peluquero.id,
                    "peluquero_nombre": peluquero.nombre,
                    "huecos": huecos_peluquero,
                })

        return huecos

    def _calcular_huecos(self, h_inicio: str, h_fin: str, turnos: List[Turno], duracion: int) -> List[dict]:
        """Calcula los huecos libres entre turnos ocupados."""
        inicio_actual = time_to_minutes(h_inicio)
        fin_jornada = time_to_minutes(h_fin)
        huecos = []

        for turno in sorted(turnos, key=lambda t: time_to_minutes(t.hora_inicio)):
            inicio_turno = time_to_minutes(turno.hora_inicio)
            if inicio_actual + duracion <= inicio_turno:
                huecos.append({
                    "hora_inicio": add_minutes("00:00", inicio_actual),
                    "hora_fin": add_minutes("00:00", inicio_turno),
                })
            inicio_actual = max(inicio_actual, time_to_minutes(turno.hora_fin))

        # Hueco después del último turno
        if inicio_actual + duracion <= fin_jornada:
            huecos.append({
                "hora_inicio": add_minutes("00:00", inicio_actual),
                "hora_fin": h_fin,
            })

        return huecos


# Importar aquí para evitar circular imports
from app.models import PeluqueroServicio
