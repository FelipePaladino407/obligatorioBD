from enum import Enum

class TipoIncidencia(str, Enum):
    INFRAESTRUCTURA = "infraestructura"
    EQUIPAMIENTO = "equipamiento"
    LIMPIEZA = "limpieza"
    RUIDO = "ruido"
    ELECTRICIDAD = "electricidad"
    OTRO = "otro"
