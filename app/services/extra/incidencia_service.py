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

def listar_incidencias_por_reportante(ci_reportante: str) -> List[IncidenciaRow]:
    """
    Devuelve todas las incidencias reportadas por un participante (según su CI),
    ordenadas de la más reciente a la más vieja.
    """
    sql = """
        SELECT *
        FROM incidencia_sala
        WHERE ci_reportante = %s
        ORDER BY fecha_reporte DESC;
    """
    return execute_query(sql, (ci_reportante,), fetch=True)

def resolver_incidencia_usuario(id_incidencia: int):
    """
    Marca la incidencia como resuelta y elimina alertas asociadas.
    (No requiere saber si es admin; eso se valida en el route)
    """
    upd = IncidenciaUpdateEstado(
        id_incidencia=id_incidencia,
        nuevo_estado=EstadoIncidencia.RESUELTA
    )
    actualizar_estado_incidencia(upd)

    sql_del = "DELETE FROM alerta_reserva WHERE id_incidencia = %s;"
    execute_query(sql_del, (id_incidencia,), fetch=False)

    return True



def delete_incidencia(id_incidencia: int) -> bool:
    """
    Elimina una incidencia y, por cascada, todas sus alertas asociadas.
    Retorna True si se eliminó, False si no existía.
    """

    # PARA VERIFICAR QUE EXISTE: UUUUUUUUUUUUUUU
    sql_check = """
        SELECT 1 FROM incidencia_sala WHERE id_incidencia = %s LIMIT 1;
    """
    exists = execute_query(sql_check, (id_incidencia,), fetch=True)
    if not exists:
        return False

    # Elimino la incidencia (las alertas se borran por ON DELETE CASCADE)
    sql_delete = "DELETE FROM incidencia_sala WHERE id_incidencia = %s;"
    execute_query(sql_delete, (id_incidencia,), fetch=False)

    return True
