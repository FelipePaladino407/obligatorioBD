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
    id_reserva: Optional[int] = None  # si la reportás desde una reserva concreta

@dataclass(frozen=True)
class IncidenciaUpdateEstado:
    id_incidencia: int
    nuevo_estado: EstadoIncidencia
    # Si quisieras log de notas/eventos de cambio, podrías agregar "nota" y crear una tabla incidencia_evento.

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
