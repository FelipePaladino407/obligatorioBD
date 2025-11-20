from __future__ import annotations
from typing import TypedDict, Literal
from app.models import reportes_model

# Enumeración de consultas soportadas por el endpoint único /v1/reportes
ConsultaID = Literal[
    # Consultas pedidas en la letra:
    "SALAS_MAS_RESERVADAS",
    "TURNOS_MAS_DEMANDADOS",
    "OCUPACION_POR_EDIFICIO",
    "RESERVAS_POR_PROGRAMA_FACULTAD",
    "UTILIZADAS_VS_CANCELADAS_NOASISTIDAS",
    "RESERVAS_Y_ASISTENCIAS_POR_ROL_Y_TIPO_PROGRAMA",
    "SANCIONES_POR_ROL_Y_TIPO_PROGRAMA",
    "PROMEDIO_PARTICIPANTES_POR_SALA",


    # Consultas propias (incidencias/alertas/estado):
    "INCIDENCIAS_ABIERTAS_POR_SALA",
    "RATIO_NO_ASISTENCIA_POR_SALA",
    "ALERTAS_POR_TIPO",
    "ESTADO_SALAS_RESUMEN",
]

class ReporteParams(TypedDict, total=False):
    desde: str
    hasta: str
    edificio: str
    facultad: str
    limit: int
    offset: int

def _validate_params(p: ReporteParams) -> ReporteParams:
    """Validaciones mínimas de filtros (formato simple y rangos)."""
    if "limit" in p:
        if p["limit"] < 1 or p["limit"] > 200:
            raise ValueError("limit debe estar entre 1 y 200")
    if "offset" in p and p["offset"] < 0:
        raise ValueError("offset no puede ser negativo")
    for k in ("desde", "hasta"):
        if p.get(k):
            v = p[k]
            if not isinstance(v, str) or len(v) != 10 or v[4] != "-" or v[7] != "-":
                raise ValueError(f"{k} debe ser YYYY-MM-DD")
    return p

def ejecutar_consulta(consulta: ConsultaID, params: ReporteParams):
    """Despacha la consulta solicitada hacia el modelo y arma el payload estándar."""
    p = _validate_params(params)

    DISPATCH = {
        # Letra:
        "SALAS_MAS_RESERVADAS": reportes_model.salas_mas_reservadas,
        "TURNOS_MAS_DEMANDADOS": reportes_model.turnos_mas_demandados,
        "OCUPACION_POR_EDIFICIO": reportes_model.ocupacion_por_edificio,
        "RESERVAS_POR_PROGRAMA_FACULTAD": reportes_model.reservas_por_programa_facultad,
        "UTILIZADAS_VS_CANCELADAS_NOASISTIDAS": reportes_model.utilizadas_vs_canceladas_noasistidas,
        "SANCIONES_POR_ROL_Y_TIPO_PROGRAMA": reportes_model.sanciones_por_rol_y_tipo_programa,
        "PROMEDIO_PARTICIPANTES_POR_SALA": reportes_model.promedio_participantes_por_sala,
        "RESERVAS_Y_ASISTENCIAS_POR_ROL_Y_TIPO_PROGRAMA": reportes_model.reservas_y_asistencias_por_rol_y_tipo_programa,

        # Propias:
        "INCIDENCIAS_ABIERTAS_POR_SALA": reportes_model.incidencias_abiertas_por_sala,
        "RATIO_NO_ASISTENCIA_POR_SALA": reportes_model.ratio_no_asistencia_por_sala,
        "ALERTAS_POR_TIPO": reportes_model.alertas_por_tipo,
        "ESTADO_SALAS_RESUMEN": reportes_model.estado_salas_resumen,
    }

    if consulta not in DISPATCH:
        raise ValueError("id_consulta inválido")

    columns, rows = DISPATCH[consulta](p)

    # CAMBI0:
    items = [dict(zip(columns, row)) for row in rows]

    return {
        "consulta_id": consulta,
        "params": p,
        "count": len(items),
        "columns": columns,   # OPCIONAL ESTO, por si el frontend quiere usarlas
        "data": items,        # / ver en Postman
    }
