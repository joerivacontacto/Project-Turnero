"""Domain models as simple dataclasses (sqlite3 row mapping)."""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Usuario:
    id: int
    username: str
    password_hash: str
    rol: str
    activo: bool
    creado_en: str

@dataclass
class Peluquero:
    id: int
    nombre: str
    activo: bool
    creado_en: str

@dataclass
class Servicio:
    id: int
    nombre: str
    duracion_min: int
    precio: int
    activo: bool
    creado_en: str

@dataclass
class Cliente:
    id: int
    nombre: str
    telefono: Optional[str]
    email: Optional[str]
    activo: bool
    creado_en: str

@dataclass
class Turno:
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
    # Joined fields
    cliente_nombre: Optional[str] = None
    peluquero_nombre: Optional[str] = None
    servicio_nombre: Optional[str] = None

@dataclass
class Horario:
    id: int
    peluquero_id: int
    dia_semana: int
    hora_inicio: str
    hora_fin: str

@dataclass
class Ausencia:
    id: int
    peluquero_id: int
    fecha_inicio: str
    fecha_fin: str
    motivo: Optional[str]
