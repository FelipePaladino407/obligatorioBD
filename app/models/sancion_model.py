from dataclasses import dataclass
from datetime import date
from typing import Optional, TypedDict, Literal

Motivo = Literal["no asistencia", "conducta", "manual"]

# -----------------------------
# Modelos de ENTRADA (input)
# -----------------------------
@dataclass(frozen=True)
class SancionCreate:
    """
    Datos necesarios para crear una sanción.
    Se corresponde con columnas de sancion_participante.
    """
    ci_participante: str
    fecha_inicio: date
    fecha_fin: date
    motivo: str = "no asistencia"  # el default de la sancion en la BD es "no asisstencia".

@dataclass(frozen=True)
class SancionKey:
    """
    Clave primaria compuesta de sancion_participante:
    (ci_participante, fecha_inicio)
    """
    ci_participante: str
    fecha_inicio: date

# -----------------------------
# Modelos de SALIDA (output)
# -----------------------------
@dataclass(frozen=True)
class SancionOut:
    """
    Cómo devolvemos una sanción hacia API/CLI.
    """
    ci_participante: str
    fecha_inicio: date
    fecha_fin: date
    motivo: Optional[str]

# -----------------------------
# Filas que vienen de la BD
# -----------------------------
class SancionRow(TypedDict):
    ci_participante: str
    fecha_inicio: date
    fecha_fin: date
    motivo: Optional[str]
