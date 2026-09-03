from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from app.schemas import ClienteCreate, ClienteUpdate, ClienteResponse
from app.auth.jwt import get_current_user, require_rol
from app.database import get_db
from app.utils.time import ahora_str

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("", response_model=List[ClienteResponse])
def listar_clientes(
    q: Optional[str] = Query(None, description="Búsqueda por nombre o teléfono"),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    if q:
        rows = db.execute(
            "SELECT * FROM clientes WHERE activo = 1 AND (nombre LIKE ? OR telefono LIKE ?) ORDER BY nombre",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre").fetchall()
    return [dict(r) for r in rows]

@router.post("", response_model=ClienteResponse, status_code=201)
def crear_cliente(data: ClienteCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    cursor = db.execute(
        "INSERT INTO clientes (nombre, telefono, email, activo, creado_en) VALUES (?, ?, ?, 1, ?)",
        (data.nombre, data.telefono, data.email, ahora_str()),
    )
    db.commit()
    row = db.execute("SELECT * FROM clientes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    row = db.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return dict(row)

@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, data: ClienteUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    row = db.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if data.nombre is not None:
        db.execute("UPDATE clientes SET nombre = ? WHERE id = ?", (data.nombre, cliente_id))
    if data.telefono is not None:
        db.execute("UPDATE clientes SET telefono = ? WHERE id = ?", (data.telefono, cliente_id))
    if data.email is not None:
        db.execute("UPDATE clientes SET email = ? WHERE id = ?", (data.email, cliente_id))
    if data.activo is not None:
        db.execute("UPDATE clientes SET activo = ? WHERE id = ?", (1 if data.activo else 0, cliente_id))
    db.commit()
    row = db.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    return dict(row)

@router.delete("/{cliente_id}", status_code=204)
def eliminar_cliente(cliente_id: int, db=Depends(get_db), current_user=Depends(require_rol("admin"))):
    row = db.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (cliente_id,))
    db.commit()
    return None
