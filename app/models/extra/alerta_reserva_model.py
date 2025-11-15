from dataclasses import dataclass
from typing import TypedDict
from app.enums.extra.tipo_alerta_reserva import TipoAlertaReserva

@dataclass(frozen=True)
class AlertaReservaCreate:
    id_reserva: int
    id_incidencia: int
    tipo_alerta: TipoAlertaReserva
    mensaje: str

class AlertaReservaRow(TypedDict, total=False):
    id_alerta: int
    id_reserva: int
    id_incidencia: int
    tipo_alerta: str
    mensaje: str
    fecha_creacion: str
    leida: int  # 0/1
