from typing import List, Dict, Any
from app.db import execute_query, execute_returning_id
from app.models.alerta_model import AlertaCreate, AlertaUpdateEstado
from app.enums.estado_alerta import EstadoAlerta

def crear_alerta(a: AlertaCreate) -> int:
    """
    Crea una alerta en estado NUEVA y devuelve id_alerta (AUTO_INCREMENT).
    """
    sql = """
        INSERT INTO alerta_sala
            (nombre_sala, edificio, tipo, prioridad, estado, descripcion, creado_por_ci)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s);
    """
    params = (
        a.nombre_sala,
        a.edificio,
        a.tipo.value,
        a.prioridad,                  # 'baja' | 'media' | 'alta' | 'critica'
        EstadoAlerta.NUEVA.value,     # no hardcodear 'nueva'
        a.descripcion,
        a.creado_por_ci,
    )
    return execute_returning_id(sql, params)

def cambiar_estado_alerta(upd: AlertaUpdateEstado) -> None:
    """
    Loguea el cambio en alerta_evento y actualiza el estado en alerta_sala.
    """
    insert_evt = """
        INSERT INTO alerta_evento (id_alerta, de_estado, a_estado, nota, hecho_por_ci)
        VALUES (%s, (SELECT estado FROM alerta_sala WHERE id_alerta=%s), %s, %s, %s);
    """
    execute_query(
        insert_evt,
        (upd.id_alerta, upd.id_alerta, upd.nuevo_estado.value, upd.nota, upd.hecho_por_ci),
        fetch=False,
    )

    upd_sql = "UPDATE alerta_sala SET estado=%s WHERE id_alerta=%s;"
    execute_query(upd_sql, (upd.nuevo_estado.value, upd.id_alerta), fetch=False)

def listar_alertas_abiertas() -> List[Dict[str, Any]]:
    """
    Devuelve alertas no resueltas, ordenadas por severidad y antigüedad.
    """
    sql = """
        SELECT *
        FROM alerta_sala
        WHERE estado NOT IN ('resuelta','falsa_alarma')
        ORDER BY FIELD(prioridad,'critica','alta','media','baja'), creado_en ASC;
    """
    return execute_query(sql, None, fetch=True)

def obtener_alerta(id_alerta: int) -> Dict[str, Any] | None:
    sql = "SELECT * FROM alerta_sala WHERE id_alerta=%s;"
    rows = execute_query(sql, (id_alerta,), fetch=True)
    return rows[0] if rows else None
