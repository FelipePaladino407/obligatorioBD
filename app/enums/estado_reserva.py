from enum import Enum

class EstadoReserva(Enum):
    ACTIVA = "activa"
    CANCELADA = "cancelada"
    SIN_ASISTENCIA = "sin_asistencia"
    FINALIZADA = "finalizada"
