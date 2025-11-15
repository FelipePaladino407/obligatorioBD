from enum import Enum

class TipoAlertaReserva(str, Enum):
    SALA_INHABILITADA = "sala_inhabilitada"
    INCONVENIENTE = "inconveniente"
    RECORDATORIO = "recordatorio"
