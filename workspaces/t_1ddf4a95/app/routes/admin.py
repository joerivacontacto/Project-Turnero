from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.auth.jwt import get_current_user, require_rol
from app.database import get_db
from app.utils.time import hoy_str

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def dashboard(db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    fecha = hoy_str()
    turnos_hoy = db.execute("SELECT * FROM turnos WHERE fecha = ?", (fecha,)).fetchall()

    pendientes = sum(1 for t in turnos_hoy if t["estado"] == "pendiente")
    confirmados = sum(1 for t in turnos_hoy if t["estado"] == "confirmado")
    completados = sum(1 for t in turnos_hoy if t["estado"] == "completado")
    cancelados = sum(1 for t in turnos_hoy if t["estado"] == "cancelado")

    proximo = db.execute(
        "SELECT * FROM turnos WHERE fecha = ? AND estado IN ('pendiente', 'confirmado') ORDER BY hora_inicio LIMIT 1",
        (fecha,),
    ).fetchone()

    peluqueros_activos = db.execute("SELECT COUNT(*) FROM peluqueros WHERE activo = 1").fetchone()[0]

    return {
        "fecha": fecha,
        "total_turnos": len(turnos_hoy),
        "pendientes": pendientes,
        "confirmados": confirmados,
        "completados": completados,
        "cancelados": cancelados,
        "proximo_turno": dict(proximo) if proximo else None,
        "peluqueros_activos": peluqueros_activos,
    }

@router.get("/export/dia")
def exportar_dia(
    fecha: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    format: str = Query("csv", pattern=r"^(csv|pdf)$"),
    db=Depends(get_db),
    current_user=Depends(require_rol("admin")),
):
    turnos = db.execute(
        """SELECT t.*, c.nombre as cliente_nombre, p.nombre as peluquero_nombre, s.nombre as servicio_nombre
           FROM turnos t
           INNER JOIN clientes c ON c.id = t.cliente_id
           INNER JOIN peluqueros p ON p.id = t.peluquero_id
           INNER JOIN servicios s ON s.id = t.servicio_id
           WHERE t.fecha = ? AND t.estado != 'cancelado'
           ORDER BY t.hora_inicio""",
        (fecha,),
    ).fetchall()

    if format == "csv":
        lines = ["id,cliente,peluquero,servicio,fecha,hora_inicio,hora_fin,estado"]
        for t in turnos:
            lines.append(
                f"{t['id']},{t['cliente_nombre']},{t['peluquero_nombre']},{t['servicio_nombre']},"
                f"{t['fecha']},{t['hora_inicio']},{t['hora_fin']},{t['estado']}"
            )
        content = "\n".join(lines)
        return {"content": content, "filename": f"agenda_{fecha}.csv"}

    return {"message": "PDF export no implementado en v1. Use format=csv.", "turnos": len(turnos)}
