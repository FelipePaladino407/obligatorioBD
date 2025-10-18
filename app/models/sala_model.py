from dataclasses import dataclass 
from typing import TypeDict

@dataclass(Frozen=True)

class SalaCreate: 
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala str # 'libre' | 'postgrado' | 'docente'

class SalaRow(TypeDict):
    nombre_sala: str
    edificio: str
    capacidad: int
    tipo_sala: str

