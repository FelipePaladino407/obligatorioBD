from enum import Enum

class EstadoIncidencia(str, Enum):
    ABIERTA = "abierta"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
