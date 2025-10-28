# ESTO ES PARA LA NUEVA FUNCIONALIDAD DE ALERTA POR SALA:
from enum import Enum
class TipoAlerta(str, Enum):
    HUMO = "humo"
    FUEGO = "fuego"
    RUIDO = "ruido"
    ROTURA = "rotura"
    OTRO = "otro"
