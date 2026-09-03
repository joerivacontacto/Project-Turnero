from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.auth.jwt import get_current_user
from app.database import get_db
from app.utils.time import time_to_minutes, add_minutes, hoy_str
from datetime import datetime, timedelta

router = APIRouter(prefix="/agenda", tags=["Agenda"])

@router.get("/dia")
def agenda_dia(
    fecha: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    peluquero_id: Optional[int] = None,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = "SELECT * FROM turnos WHERE fecha = ? AND estado != 'cancelado'"
    params = [fecha]
    if peluquero_id:
        query += " AND peluquero_id = ?"
        params.append(peluquero_id)
    query += " ORDER BY hora_inicio"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@router.get("/semana")
def agenda_semana(
    fecha: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    dt = datetime.strptime(fecha, "%Y-%m-%d")
    inicio_semana = dt - timedelta(days=dt.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    rows = db.execute(
        "SELECT * FROM turnos WHERE fecha >= ? AND fecha <= ? AND estado != 'cancelado' ORDER BY fecha, hora_inicio",
        (inicio_semana.strftime("%Y-%m-%d"), fin_semana.strftime("%Y-%m-%d")),
    ).fetchall()

    dias = {}
    for row in rows:
        f = row["fecha"]
        if f not in dias:
            dias[f] = []
        dias[f].append(dict(row))

    resultado = []
    for i in range(7):
        dia = (inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d")
        resultado.append({"fecha": dia, "turnos": dias.get(dia, [])})
    return resultado

@router.get("/disponibilidad")
def disponibilidad(
    fecha: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    servicio_id: int = Query(...),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    servicio = db.execute("SELECT * FROM servicios WHERE id = ? AND activo = 1", (servicio_id,)).fetchone()
    if not servicio:
        return []

    dt = datetime.strptime(fecha, "%Y-%m-%d")
    dia_semana = dt.weekday()

    peluqueros = db.execute(
        """SELECT p.* FROM peluqueros p
           INNER JOIN peluqueros_servicios ps ON ps.peluquero_id = p.id
           WHERE ps.servicio_id = ? AND p.activo = 1""",
        (servicio_id,),
    ).fetchall()

    huecos = []
    for peluquero in peluqueros:
        horario = db.execute(
            "SELECT * FROM horarios WHERE peluquero_id = ? AND dia_semana = ?",
            (peluquero["id"], dia_semana),
        ).fetchone()
        if not horario:
            continue

        ausencia = db.execute(
            "SELECT * FROM ausencias WHERE peluquero_id = ? AND fecha_inicio <= ? AND fecha_fin >= ?",
            (peluquero["id"], fecha, fecha),
        ).fetchone()
        if ausencia:
            continue

        turnos_ocupados = db.execute(
            "SELECT * FROM turnos WHERE peluquero_id = ? AND fecha = ? AND estado != 'cancelado' ORDER BY hora_inicio",
            (peluquero["id"], fecha),
        ).fetchall()

        huecos_peluquero = _calcular_huecos(
            horario["hora_inicio"], horario["hora_fin"], turnos_ocupados, servicio["duracion_min"]
        )

        if huecos_peluquero:
            huecos.append({
                "peluquero_id": peluquero["id"],
                "peluquero_nombre": peluquero["nombre"],
                "huecos": huecos_peluquero,
            })

    return huecos

def _calcular_huecos(h_inicio, h_fin, turnos, duracion):
    inicio_actual = time_to_minutes(h_inicio)
    fin_jornada = time_to_minutes(h_fin)
    huecos = []

    for turno in turnos:
        inicio_turno = time_to_minutes(turno["hora_inicio"])
        if inicio_actual + duracion <= inicio_turno:
            huecos.append({
                "hora_inicio": add_minutes("00:00", inicio_actual),
                "hora_fin": add_minutes("00:00", inicio_turno),
            })
        inicio_actual = max(inicio_actual, time_to_minutes(turno["hora_fin"]))

    if inicio_actual + duracion <= fin_jornada:
        huecos.append({
            "hora_inicio": add_minutes("00:00", inicio_actual),
            "hora_fin": h_fin,
        })

    return huecos
