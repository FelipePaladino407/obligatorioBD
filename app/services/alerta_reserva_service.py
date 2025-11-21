from typing import List, Dict
from app.db import execute_query

def listar_alertas_usuario(correo: str) -> List[Dict]:
    """
    Devuelve todas las alertas asociadas a reservas en las que participa
    el usuario cuyo correo se pasa por parámetro.
    """
    sql = """
        SELECT ar.id_alerta,
               ar.tipo_alerta,
               ar.mensaje,
               ar.fecha_creacion,
               ar.leida,
               ar.id_reserva,
               i.descripcion AS incidencia_descripcion,
               i.gravedad    AS incidencia_gravedad,
               i.estado      AS incidencia_estado
        FROM alerta_reserva ar
        JOIN reserva r ON r.id_reserva = ar.id_reserva
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        JOIN participante p ON p.ci = rp.ci_participante
        JOIN incidencia_sala i ON i.id_incidencia = ar.id_incidencia
        WHERE p.email = %s
        ORDER BY ar.fecha_creacion DESC;
    """
    return execute_query(sql, (correo,), fetch=True)
