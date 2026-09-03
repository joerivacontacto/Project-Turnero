from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import ServicioCreate, ServicioUpdate, ServicioResponse
from app.auth.jwt import get_current_user, require_rol
from app.database import get_db
from app.utils.time import ahora_str

router = APIRouter(prefix="/servicios", tags=["Servicios"])

@router.get("", response_model=List[ServicioResponse])
def listar_servicios(db=Depends(get_db), current_user=Depends(get_current_user)):
    rows = db.execute("SELECT * FROM servicios WHERE activo = 1").fetchall()
    return [dict(r) for r in rows]

@router.post("", response_model=ServicioResponse, status_code=201)
def crear_servicio(data: ServicioCreate, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    cursor = db.execute(
        "INSERT INTO servicios (nombre, duracion_min, precio, activo, creado_en) VALUES (?, ?, ?, 1, ?)",
        (data.nombre, data.duracion_min, data.precio, ahora_str()),
    )
    db.commit()
    row = db.execute("SELECT * FROM servicios WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)

@router.put("/{servicio_id}", response_model=ServicioResponse)
def actualizar_servicio(servicio_id: int, data: ServicioUpdate, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM servicios WHERE id = ?", (servicio_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    if data.nombre is not None:
        db.execute("UPDATE servicios SET nombre = ? WHERE id = ?", (data.nombre, servicio_id))
    if data.duracion_min is not None:
        db.execute("UPDATE servicios SET duracion_min = ? WHERE id = ?", (data.duracion_min, servicio_id))
    if data.precio is not None:
        db.execute("UPDATE servicios SET precio = ? WHERE id = ?", (data.precio, servicio_id))
    if data.activo is not None:
        db.execute("UPDATE servicios SET activo = ? WHERE id = ?", (1 if data.activo else 0, servicio_id))
    db.commit()
    row = db.execute("SELECT * FROM servicios WHERE id = ?", (servicio_id,)).fetchone()
    return dict(row)

@router.delete("/{servicio_id}", status_code=204)
def eliminar_servicio(servicio_id: int, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM servicios WHERE id = ?", (servicio_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.execute("UPDATE servicios SET activo = 0 WHERE id = ?", (servicio_id,))
    db.commit()
    return None
