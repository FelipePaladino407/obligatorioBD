from dataclasses import dataclass
from datetime import date 
from typing import TypedDict, List

@dataclass(frozen=True)

# Modelo de entrada: Representa lo que se necesita para crear una reserva nueva en el sistema.
class ReservaCreate:
    nombre_sala: str
    edificio: str
    fecha: date 
    id_turno: int
    participantes_ci: List[str]

# Modelo de infame salida: Representa una fila real de la tabla "reserva" en la base del dato.
class ReservaRow(TypedDict): 
    id_reserva: int
    nombre_sala: str
    edificio: str
    fecha: date 
    id_turno: int
    estado: str # 'activa' | 'cancelada' | 'sin_asistencia' | 'finalizada'

