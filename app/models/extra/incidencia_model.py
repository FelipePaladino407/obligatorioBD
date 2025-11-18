from dataclasses import dataclass
from typing import Optional, TypedDict
from app.enums.extra.tipo_incidencia import TipoIncidencia
from app.enums.extra.gravedad_incidencia import GravedadIncidencia
from app.enums.extra.estado_incidencia import EstadoIncidencia

@dataclass(frozen=True)
class IncidenciaCreate:
    nombre_sala: str
    edificio: str
    ci_reportante: str
    tipo: TipoIncidencia
    gravedad: GravedadIncidencia
    descripcion: str
    id_reserva: Optional[int] = None

@dataclass(frozen=True)
class IncidenciaUpdateEstado:
    id_incidencia: int
    nuevo_estado: EstadoIncidencia


class IncidenciaRow(TypedDict, total=False):
    id_incidencia: int
    nombre_sala: str
    edificio: str
    id_reserva: int | None
    ci_reportante: str
    tipo: str
    gravedad: str
    descripcion: str
    estado: str
    fecha_reporte: str
    fecha_resolucion: str | None
