from enum import Enum

"""
Permite identificar tipo de sala (comentario inútil)
"""
class TipoSala(Enum):
    USO_LIBRE = "libre" 
    POSGRADO = "exclusiva_posgrado" 
    DOCENTES = "exclusiva_docente" 
