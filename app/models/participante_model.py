from dataclasses import dataclass 
from typing import TypedDict

@dataclass(frozen=True)

class ParticipanteCreate: 
    ci: str
    nombre: str
    apellido: str
    email: str

class ParticipanteRow(TypedDict): 
    ci: str
    nombre: str
    apallido: str
    email: str
