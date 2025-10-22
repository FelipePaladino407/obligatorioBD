from dataclasses import dataclass 
from typing import TypedDict
from app.enums.tipo_sala import TipoSala

@dataclass(frozen=True)

class SalaCreate: 
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: TipoSala # 'libre' | 'postgrado' | 'docente'

class SalaRow(TypedDict):
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: TipoSala 

