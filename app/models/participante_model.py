from dataclasses import dataclass 
from typing import Optional, TypedDict

@dataclass(frozen=True)

class ParticipanteCreate: 
    ci: str
    nombre: str
    apellido: str
    email: str

class ParticipanteRow(TypedDict): 
    ci: str
    nombre: str
    apellido: str
    email: str

@dataclass(frozen=True)
class ParticipanteUpdate:
    ci: str # obligueta
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
