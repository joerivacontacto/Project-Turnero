from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import (
    PeluqueroCreate, PeluqueroUpdate, PeluqueroResponse,
    HorarioCreate, HorarioResponse, AusenciaCreate, AusenciaResponse,
)
from app.auth.jwt import get_current_user, require_rol
from app.database import get_db
from app.utils.time import ahora_str

router = APIRouter(prefix="/peluqueros", tags=["Peluqueros"])

@router.get("", response_model=List[PeluqueroResponse])
def listar_peluqueros(db=Depends(get_db), current_user=Depends(get_current_user)):
    rows = db.execute("SELECT * FROM peluqueros WHERE activo = 1").fetchall()
    return [dict(r) for r in rows]

@router.post("", response_model=PeluqueroResponse, status_code=201)
def crear_peluquero(data: PeluqueroCreate, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    cursor = db.execute(
        "INSERT INTO peluqueros (nombre, activo, creado_en) VALUES (?, 1, ?)",
        (data.nombre, ahora_str()),
    )
    db.commit()
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)

@router.get("/{peluquero_id}", response_model=PeluqueroResponse)
def obtener_peluquero(peluquero_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (peluquero_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Peluquero no encontrado")
    return dict(row)

@router.put("/{peluquero_id}", response_model=PeluqueroResponse)
def actualizar_peluquero(peluquero_id: int, data: PeluqueroUpdate, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (peluquero_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Peluquero no encontrado")
    if data.nombre is not None:
        db.execute("UPDATE peluqueros SET nombre = ? WHERE id = ?", (data.nombre, peluquero_id))
    if data.activo is not None:
        db.execute("UPDATE peluqueros SET activo = ? WHERE id = ?", (1 if data.activo else 0, peluquero_id))
    db.commit()
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (peluquero_id,)).fetchone()
    return dict(row)

@router.delete("/{peluquero_id}", status_code=204)
def eliminar_peluquero(peluquero_id: int, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (peluquero_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Peluquero no encontrado")
    db.execute("UPDATE peluqueros SET activo = 0 WHERE id = ?", (peluquero_id,))
    db.commit()
    return None

@router.put("/{peluquero_id}/horarios")
def definir_horarios(peluquero_id: int, horarios: List[HorarioCreate], db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (peluquero_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Peluquero no encontrado")
    db.execute("DELETE FROM horarios WHERE peluquero_id = ?", (peluquero_id,))
    for h in horarios:
        db.execute(
            "INSERT INTO horarios (peluquero_id, dia_semana, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)",
            (peluquero_id, h.dia_semana, h.hora_inicio, h.hora_fin),
        )
    db.commit()
    return {"ok": True, "horarios": len(horarios)}

@router.post("/{peluquero_id}/ausencias", response_model=AusenciaResponse, status_code=201)
def marcar_ausencia(peluquero_id: int, data: AusenciaCreate, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM peluqueros WHERE id = ?", (peluquero_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Peluquero no encontrado")
    cursor = db.execute(
        "INSERT INTO ausencias (peluquero_id, fecha_inicio, fecha_fin, motivo) VALUES (?, ?, ?, ?)",
        (peluquero_id, data.fecha_inicio, data.fecha_fin, data.motivo),
    )
    db.commit()
    row = db.execute("SELECT * FROM ausencias WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)
