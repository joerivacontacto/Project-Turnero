from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas import LoginRequest, TokenResponse, UsuarioResponse
from app.auth.jwt import verify_password, create_access_token, hash_password, get_current_user
from app.database import get_db
from app.utils.time import ahora_str

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db=Depends(get_db)):
    row = db.execute("SELECT * FROM usuarios WHERE username = ?", (data.username,)).fetchone()
    if not row or not verify_password(data.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not row["activo"]:
        raise HTTPException(status_code=401, detail="Usuario inactivo")
    token = create_access_token({"sub": row["username"], "rol": row["rol"]})
    return TokenResponse(access_token=token, rol=row["rol"])

@router.post("/register", response_model=UsuarioResponse, status_code=201)
def register(data: LoginRequest, db=Depends(get_db)):
    existing = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    if existing > 0:
        raise HTTPException(status_code=403, detail="Ya existe un usuario. Use el login.")
    db.execute(
        "INSERT INTO usuarios (username, password_hash, rol, activo, creado_en) VALUES (?, ?, 'admin', 1, ?)",
        (data.username, hash_password(data.password), ahora_str()),
    )
    db.commit()
    row = db.execute("SELECT * FROM usuarios WHERE username = ?", (data.username,)).fetchone()
    return dict(row)

@router.get("/me", response_model=UsuarioResponse)
def me(current_user=Depends(get_current_user)):
    return current_user
