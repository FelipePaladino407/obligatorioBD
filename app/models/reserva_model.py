from dataclasses import dataclass
from datetime import date 
from typing import Optional, TypedDict, List
from app.enums.estado_reserva import EstadoReserva

@dataclass(frozen=True)

# Modelo de entrada: Representa lo que se necesita para crear una reserva nueva en el sistema.
class ReservaCreate:
    nombre_sala: str
    edificio: str
    fecha: date 
    id_turno: int
    estado: EstadoReserva # 'activa' | 'cancelada' | 'sin_asistencia' | 'finalizada'
    participantes_ci: List[str]

# Modelo de infame salida: Representa una fila real de la tabla "reserva" en la base del dato.
class ReservaRow(TypedDict): 
    id_reserva: int
    nombre_sala: str
    edificio: str
    fecha: date 
    id_turno: int
    estado: EstadoReserva # 'activa' | 'cancelada' | 'sin_asistencia' | 'finalizada'

@dataclass(frozen=True)
class ReservaUpdate:
    id_reserva: int  # obligatorio (no te pases de vivo) 
    nombre_sala: Optional[int] = None
    edificio: Optional[str] = None
    fecha: Optional[date] = None
    id_turno: Optional[int] = None
    estado: Optional[EstadoReserva] = None
