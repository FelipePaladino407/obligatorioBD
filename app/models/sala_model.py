from dataclasses import dataclass
from typing import Optional, TypedDict
from app.enums.tipo_sala import TipoSala
from typing import Literal

EstadoOperativo = Literal["operativa", "con_inconvenientes", "fuera_de_servicio"] # Novedad.

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
    estado: EstadoOperativo

# +++ NUEVO: fila para lecturas de estado (VIEW o fallback)
class SalaEstadoRow(TypedDict, total=False):
    nombre_sala: str
    edificio: str
    estado_calculado: EstadoOperativo  # Lo calcula automáticamente la base de datos según las incidencias abiertas de la sala.
    estado_manual:    EstadoOperativo  # Es un estado que fija un administrador directamente en la tabla sala.

