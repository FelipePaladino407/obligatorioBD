from dataclasses import dataclass
from typing import Optional, TypedDict
from app.enums.tipo_sala import TipoSala

# -------------------------
# Modelo para INSERT (crear sala)
# -------------------------
@dataclass(frozen=True)
class SalaCreate:
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: TipoSala  # ENUM: 'libre' | 'posgrado' | 'docente'

# -------------------------
# Modelo dedicado a la PK (clave compuesta)
# -------------------------
@dataclass(frozen=True)
class SalaKey:
    nombre_sala: str
    edificio: str

# -------------------------
# Modelo para UPDATE parcial
# -------------------------
@dataclass(frozen=True)
class SalaUpdate:
    nombre_sala: str
    edificio: str
    capacidad: Optional[int] = None
    tipo_sala: Optional[TipoSala] = None

# -------------------------
# Representación de fila que viene de la BD
# -------------------------
class SalaRow(TypedDict):
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: TipoSala
