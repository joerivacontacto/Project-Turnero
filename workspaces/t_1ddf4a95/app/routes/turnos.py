from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from app.schemas import TurnoCreate, TurnoUpdateEstado, TurnoResponse
from app.auth.jwt import get_current_user, require_rol
from app.services.turno_service import TurnoService
from app.database import get_db

router = APIRouter(prefix="/turnos", tags=["Turnos"])

@router.get("", response_model=List[TurnoResponse])
def listar_turnos(
    fecha: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    cliente_id: Optional[int] = None,
    peluquero_id: Optional[int] = None,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TurnoService(db)
    return service.listar_turnos(fecha=fecha, cliente_id=cliente_id, peluquero_id=peluquero_id)

@router.post("", response_model=TurnoResponse, status_code=201)
def crear_turno(data: TurnoCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = TurnoService(db)
    turno, error = service.crear_turno(data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return turno

@router.get("/{turno_id}", response_model=TurnoResponse)
def obtener_turno(turno_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = TurnoService(db)
    turno = service.obtener_turno(turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return turno

@router.put("/{turno_id}/estado", response_model=TurnoResponse)
def cambiar_estado(turno_id: int, data: TurnoUpdateEstado, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = TurnoService(db)
    turno, error = service.cambiar_estado(turno_id, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return turno

@router.delete("/{turno_id}", status_code=204)
def cancelar_turno(turno_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = TurnoService(db)
    ok, error = service.cancelar_turno(turno_id)
    if not ok:
        raise HTTPException(status_code=400, detail=error)
    return None
