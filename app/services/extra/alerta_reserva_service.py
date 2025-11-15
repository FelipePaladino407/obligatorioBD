from typing import List, Dict, Any, Optional
from app.db import execute_query, execute_returning_id
from app.enums.extra.tipo_alerta_reserva import TipoAlertaReserva
from app.models.extra.alerta_reserva_model import AlertaReservaCreate, AlertaReservaRow

def crear_alerta_reserva(a: AlertaReservaCreate) -> int:
    sql = """
        INSERT INTO alerta_reserva
            (id_reserva, id_incidencia, tipo_alerta, mensaje)
        VALUES
            (%s, %s, %s, %s);
    """
    params = (a.id_reserva, a.id_incidencia, a.tipo_alerta.value, a.mensaje)
    return execute_returning_id(sql, params)

def listar_alertas_de_reserva(id_reserva: int, solo_no_leidas: bool = False) -> List[AlertaReservaRow]:
    base = "SELECT * FROM alerta_reserva WHERE id_reserva=%s"
    if solo_no_leidas:
        base += " AND leida = FALSE"
    base += " ORDER BY fecha_creacion ASC;"
    return execute_query(base, (id_reserva,), fetch=True)

def marcar_alerta_leida(id_alerta: int) -> None:
    sql = "UPDATE alerta_reserva SET leida=TRUE WHERE id_alerta=%s;"
    execute_query(sql, (id_alerta,), fetch=False)

def propagar_alertas_por_incidencia(
    id_incidencia: int,
    nombre_sala: str,
    edificio: str,
    gravedad: str,
    mensaje_base: str
) -> int:
    """
    Busca reservas futuras activas de la sala afectada y crea alertas por cada una.
    Retorna cuántas alertas creó.
    """
    # tipo de alerta según gravedad
    tipo = (TipoAlertaReserva.SALA_INHABILITADA
            if gravedad == "alta"
            else TipoAlertaReserva.INCONVENIENTE)

    # Reservas activas desde hoy en adelante
    sql_res = """
        SELECT id_reserva, fecha, id_turno
        FROM reserva
        WHERE nombre_sala=%s AND edificio=%s
          AND fecha >= CURDATE()
          AND estado = 'activa';
    """
    reservas = execute_query(sql_res, (nombre_sala, edificio), fetch=True)

    creadas = 0
    for r in reservas:
        msg = f"{mensaje_base} (Reserva {r['id_reserva']} - {r['fecha']} turno {r['id_turno']})"
        crear_alerta_reserva(AlertaReservaCreate(
            id_reserva=r["id_reserva"],
            id_incidencia=id_incidencia,
            tipo_alerta=tipo,
            mensaje=msg
        ))
        creadas += 1
    return creadas
