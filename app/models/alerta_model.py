from dataclasses import dataclass
from typing import Optional, TypedDict
from app.enums.tipo_alerta import TipoAlerta
from app.enums.estado_alerta import EstadoAlerta

@dataclass(frozen=True)
class AlertaCreate:
    nombre_sala: str
    edificio: str
    tipo: TipoAlerta
    prioridad: str = "media"      # 'baja' | 'media' | 'alta' | 'critica'
    descripcion: Optional[str] = None
    creado_por_ci: Optional[str] = None

@dataclass(frozen=True)
class AlertaUpdateEstado:
    id_alerta: int
    nuevo_estado: EstadoAlerta
    nota: Optional[str] = None
    hecho_por_ci: Optional[str] = None

class AlertaRow(TypedDict):
    id_alerta: int
    nombre_sala: str
    edificio: str
    tipo: str
    prioridad: str
    estado: str
    descripcion: str | None
    creado_por_ci: str | None
