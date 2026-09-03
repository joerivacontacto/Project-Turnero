from pydantic import BaseModel, Field
from typing import Optional, List

# --- Auth schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str

class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: str
    activo: bool
    creado_en: str

# --- Peluquero schemas ---
class PeluqueroBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)

class PeluqueroCreate(PeluqueroBase):
    pass

class PeluqueroUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    activo: Optional[bool] = None

class PeluqueroResponse(BaseModel):
    id: int
    nombre: str
    activo: bool
    creado_en: str

# --- Servicio schemas ---
class ServicioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    duracion_min: int = Field(..., gt=0, le=480)
    precio: int = Field(0, ge=0)

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    duracion_min: Optional[int] = Field(None, gt=0, le=480)
    precio: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class ServicioResponse(BaseModel):
    id: int
    nombre: str
    duracion_min: int
    precio: int
    activo: bool
    creado_en: str

# --- Cliente schemas ---
class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    telefono: Optional[str]
    email: Optional[str]
    activo: bool
    creado_en: str

# --- Horario schemas ---
class HorarioBase(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6)
    hora_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    hora_fin: str = Field(..., pattern=r"^\d{2}:\d{2}$")

class HorarioCreate(HorarioBase):
    pass

class HorarioResponse(BaseModel):
    id: int
    peluquero_id: int
    dia_semana: int
    hora_inicio: str
    hora_fin: str

# --- Ausencia schemas ---
class AusenciaBase(BaseModel):
    fecha_inicio: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    fecha_fin: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    motivo: Optional[str] = Field(None, max_length=200)

class AusenciaCreate(AusenciaBase):
    pass

class AusenciaResponse(BaseModel):
    id: int
    peluquero_id: int
    fecha_inicio: str
    fecha_fin: str
    motivo: Optional[str]

# --- Turno schemas ---
class TurnoBase(BaseModel):
    cliente_id: int
    peluquero_id: int
    servicio_id: int
    fecha: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    hora_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    hora_fin: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    tolerancia_min: int = Field(5, ge=0, le=60)

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdateEstado(BaseModel):
    estado: str = Field(..., pattern=r"^(pendiente|confirmado|en_curso|completado|cancelado)$")

class TurnoResponse(BaseModel):
    id: int
    cliente_id: int
    peluquero_id: int
    servicio_id: int
    fecha: str
    hora_inicio: str
    hora_fin: str
    estado: str
    tolerancia_min: int
    creado_en: str
