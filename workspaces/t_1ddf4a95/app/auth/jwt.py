"""Authentication utilities using PyJWT and hashlib."""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import get_settings
from app.database import get_db

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256 with random salt."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return f"{salt}${pw_hash}"

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, stored_hash = hashed.split("$", 1)
        pw_hash = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt.encode(), 100000).hex()
        return secrets.compare_digest(pw_hash, stored_hash)
    except (ValueError, AttributeError):
        return False

def create_access_token(data: dict, expires_hours: Optional[int] = None) -> str:
    to_encode = data.copy()
    hours = expires_hours or settings.JWT_EXPIRE_HOURS
    expire = datetime.utcnow() + timedelta(hours=hours)
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = pyjwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db),
):
    """Get current user from JWT token."""
    from app.models import Usuario
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    # Query using sqlite3
    conn = db
    row = conn.execute(
        "SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return _row_to_usuario(row)

def require_rol(*roles: str):
    def dependency(current_user=Depends(get_current_user)):
        if current_user["rol"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {', '.join(roles)}",
            )
        return current_user
    return dependency

def _row_to_usuario(row) -> dict:
    return {
        "id": row["id"],
        "username": row["username"],
        "rol": row["rol"],
        "activo": bool(row["activo"]),
        "creado_en": row["creado_en"],
    }
