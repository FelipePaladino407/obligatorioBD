from typing import List, Dict, Any, Optional
from app.db import execute_query, execute_returning_id
from app.models.extra.incidencia_model import (
    IncidenciaCreate, IncidenciaUpdateEstado, IncidenciaRow
)
from app.enums.extra.estado_incidencia import EstadoIncidencia

def crear_incidencia(data: IncidenciaCreate) -> int:
    """
    Crea una incidencia de sala en estado 'abierta'.
    (La validación de que el reportante tenga reserva activa se hace del lado del controlador)
    """
    sql = """
        INSERT INTO incidencia_sala
            (nombre_sala, edificio, id_reserva, ci_reportante,
             tipo, gravedad, descripcion, estado)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, 'abierta');
    """
    params = (
        data.nombre_sala,
        data.edificio,
        data.id_reserva,
        data.ci_reportante,
        data.tipo.value,
        data.gravedad.value,
        data.descripcion,
    )
    return execute_returning_id(sql, params)

def actualizar_estado_incidencia(upd: IncidenciaUpdateEstado) -> None:
    """
    Actualiza el estado de la incidencia. Si pasa a 'resuelta', setea fecha_resolucion.
    """
    if upd.nuevo_estado == EstadoIncidencia.RESUELTA:
        sql = "UPDATE incidencia_sala SET estado=%s, fecha_resolucion=NOW() WHERE id_incidencia=%s;"
        params = (upd.nuevo_estado.value, upd.id_incidencia)
    else:
        sql = "UPDATE incidencia_sala SET estado=%s WHERE id_incidencia=%s;"
        params = (upd.nuevo_estado.value, upd.id_incidencia)
    execute_query(sql, params, fetch=False)

def obtener_incidencia(id_incidencia: int) -> Optional[IncidenciaRow]:
    sql = "SELECT * FROM incidencia_sala WHERE id_incidencia=%s;"
    rows = execute_query(sql, (id_incidencia,), fetch=True)
    return rows[0] if rows else None

def listar_incidencias_abiertas() -> List[IncidenciaRow]:
    sql = """
        SELECT *
        FROM incidencia_sala
        WHERE estado <> 'resuelta'
        ORDER BY FIELD(gravedad,'alta','media','baja'), fecha_reporte ASC;
    """
    return execute_query(sql, None, fetch=True)

def listar_incidencias_por_sala(nombre_sala: str, edificio: str) -> List[IncidenciaRow]:
    sql = """
        SELECT *
        FROM incidencia_sala
        WHERE nombre_sala=%s AND edificio=%s
        ORDER BY fecha_reporte DESC;
    """
    return execute_query(sql, (nombre_sala, edificio), fetch=True)
