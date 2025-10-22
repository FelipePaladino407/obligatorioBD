from dataclasses import dataclass 
from typing import TypedDict

@dataclass(frozen=True)

class SalaCreate: 
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: str # 'libre' | 'postgrado' | 'docente'

class SalaRow(TypedDict):
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: str

