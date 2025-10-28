# ESTO ES PARA LA NUEVA FUNCIONALIDAD DE ALERTA POR SALA:
from enum import Enum
class EstadoAlerta(str, Enum):
    NUEVA = "nueva"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    FALSA_ALARMA = "falsa_alarma"
