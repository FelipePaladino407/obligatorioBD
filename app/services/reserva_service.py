from datetime import date
from re import error
from typing import Dict, List, cast

from flask import jsonify, request

from app.auth import required_token
from app.db import execute_query, execute_returning_id
from app.enums.tipo_sala import TipoSala
from app.enums.tipo_usuario import TipoUsuario
from app.models.participante_model import ParticipanteRow
from app.models.reserva_model import ReservaCreate, ReservaRow, ReservaUpdate
from app.enums.estado_reserva import EstadoReserva
from app.services.participante_service import get_participante_rol
from app.services.sala_service import get_sala, get_tipo_sala


def create_reserva(r: ReservaCreate, force: bool = False) -> int:
    """
    Crea una reserva con validaciones:
      - No permite reservar sala fuera de servicio
      - Muestra advertencia si la sala tiene inconvenientes (requiere force=True)
      - Valida capacidad, roles y límites semanales/diarios
    """

    # ======================================================
    # 0) Validación de estado de sala (calculado + manual)
    # ======================================================
    sql_estado = """
        SELECT estado_manual, estado_calculado
        FROM vista_estado_sala
        WHERE nombre_sala = %s AND edificio = %s
        LIMIT 1;
    """
    row_estado = execute_query(sql_estado, (r.nombre_sala, r.edificio), fetch=True)

    if not row_estado:
        raise Exception("La sala no existe.")

    estado_manual = row_estado[0]["estado_manual"]
    estado_calculado = row_estado[0]["estado_calculado"]

    # ❌ BLOQUEAR reserva si sala está fuera de servicio (manual o calculado)
    if estado_manual == "fuera_de_servicio" or estado_calculado == "fuera_de_servicio":
        raise Exception("La sala está fuera de servicio y no se puede reservar.")

    # ⚠ Advertencia si está con inconvenientes y NO vino force=true
    if (estado_manual == "con_inconvenientes" or estado_calculado == "con_inconvenientes") and not force:
        sql_incidencias = """
            SELECT descripcion, gravedad
            FROM incidencia_sala
            WHERE nombre_sala = %s
              AND edificio = %s
              AND estado <> 'resuelta';
        """
        incidencias = execute_query(
            sql_incidencias, (r.nombre_sala, r.edificio), fetch=True
        )

        raise Warning({
            "warning": "La sala tiene inconvenientes.",
            "incidencias": incidencias,
            "action": "Reenviar reserva con force=true para confirmar."
        })

    # ======================================================
    # Validaciones existentes (ya estaban en tu servicio)
    # ======================================================
    validar_capacidad(r)
    validar_participantes_rol_sala(r)
    validar_cantidad_reservas(r)

    # ======================================================
    # Crear reserva
    # ======================================================
    query_reserva = """
        INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado)
        VALUES (%s, %s, %s, %s, %s);
    """

    params_reserva = (
        r.nombre_sala,
        r.edificio,
        r.fecha,
        r.id_turno,
        r.estado,
    )

    id_reserva = execute_returning_id(query_reserva, params_reserva)

    query_participante = """
        INSERT INTO reserva_participante (ci_participante, id_reserva, asistencia)
        VALUES (%s, %s, %s);
    """

    for ci in r.participantes_ci:
        params_participante = (ci, id_reserva, False)
        execute_query(query_participante, params_participante, fetch=False)

    return id_reserva


def remove_reserva(id: int) -> None:
    """
    Elimina una instancia de reserva en base a su id
    Args:
        id (int): id de la reserva en cuestión
    """
    query: str = """
    DELETE FROM reserva WHERE id_reserva = %s;
    """
    params: tuple[int] = (id,)
    execute_query(query, params, fetch=False, is_admin=True)

def list_reservas() -> List[ReservaRow]:
    """
    Devuelve todas las reservas en la base del dato
    Returns:
        List[ParticipanteRow]: Lista completa de instancias de reserva
    """
    query: str = """
    SELECT * FROM reserva;
    """
    result: List[Dict] = execute_query(query, None, fetch=True) 
    return cast(List[ReservaRow], result)

def update_reserva(update: ReservaUpdate) -> None:
    """
    Modifica una reserva recibiendo un nuevo modelo de reserva
    Args:
        update (ReservaUpdate): Un nuevo modelo donde cada atributo distinto de None es modificado en la base del Dato
    """
    query: str = "UPDATE reserva SET "
    params = []
    updates = []

    if update.nombre_sala is not None:
        updates.append("nombre_sala = %s")
        params.append(update.nombre_sala)
    if update.fecha is not None:
        updates.append("fecha = %s")
        params.append(update.fecha)
    if update.edificio is not None:
        updates.append("edificio = %s")
        params.append(update.edificio)
    if update.id_turno is not None:
        updates.append("id_turno = %s")
        params.append(update.id_turno)
    if update.estado is not None:
        updates.append("estado = %s")
        params.append(update.estado)

    if not updates:
        return  # nada nadonga 

    query += ", ".join(updates) + " WHERE id_reserva = %s"
    params.append(update.id_reserva)
    execute_query(query, tuple(params), fetch=False)

    
def validar_participantes_rol_sala(r: ReservaCreate):
    tipo_sala = get_sala(r.nombre_sala, r.edificio)["tipo_sala"]

    for p in r.participantes_ci:
        rol = get_participante_rol(p)

        if tipo_sala == "uso_libre":
            continue

        if tipo_sala == "posgrado" and rol not in ("docente", "estudiante_posgrado"):
            raise error("Solo docentes y posgrado pueden reservar esta sala")

        if tipo_sala == "docente" and rol != "docente":
            raise error("Solo docentes pueden reservar esta sala")

def validar_capacidad(r: ReservaCreate):
    cap: int = int(get_sala(r.nombre_sala, r.edificio)["capacidad"])

    if len(r.participantes_ci) > cap:
        raise error("Son muchos, vayanse")


def validar_cantidad_reservas(r: ReservaCreate):
    """
    Verifica límites para participantes 'estudiante_grado':
      - máximo 2 horas por día (equivale a 2 turnos por día)
      - máximo 3 reservas activas por semana

    Implementación:
      - Para cada participante que sea 'estudiante_grado' se consultan 
      las reservas activas existentes en la misma fecha (día) y en la misma semana.
      - Como cada turno es 1 hora, 1 reserva = 1 hora. (eguro)
      - Si al sumar la nueva reserva se excede el límite, tira un error fatal mortal.
    """

    daily_query = """
    SELECT COUNT(*) AS cnt
    FROM reserva rs
    JOIN reserva_participante rp ON rs.id_reserva = rp.id_reserva
    WHERE rp.ci_participante = %s
      AND rs.fecha = %s
      AND rs.estado = 'activa';
    """

    weekly_query = """
    SELECT COUNT(*) AS cnt
    FROM reserva rs
    JOIN reserva_participante rp ON rs.id_reserva = rp.id_reserva
    WHERE rp.ci_participante = %s
      AND YEARWEEK(rs.fecha, 3) = YEARWEEK(%s, 3)
      AND rs.estado = 'activa';
    """

    for ci in r.participantes_ci:
        rol = get_participante_rol(ci)
        # solo aplico límites a estudiantes de grado
        if rol != "estudiante_grado":
            # dale nomá
            continue

        # conteo diario (solución inteligente)
        res_daily = execute_query(daily_query, (ci, r.fecha), fetch=True)
        daily_cnt = 0
        if res_daily:
            daily_cnt = int(res_daily[0]["cnt"])

        # cada reserva añade 1 turno (1 hora), por eso compruebo +1
        if daily_cnt + 1 > 2:
            raise error(f"El participante {ci} superaría las 2 horas en la fecha {r.fecha} (ya tiene {daily_cnt}).")

        # conteo semanal (solo reservas activas)
        res_weekly = execute_query(weekly_query, (ci, r.fecha), fetch=True)
        weekly_cnt = 0
        if res_weekly:
            weekly_cnt = int(res_weekly[0]["cnt"])

        if weekly_cnt + 1 > 3:
            raise error(f"El participante {ci} superaría las 3 reservas activas en la semana de {r.fecha} (ya tiene {weekly_cnt}).")

# def validar_cantidad_reservas(r: ReservaCreate):
#     raise error("pa")


def list_reservas_usuario(correo: str):
    """
    Devuelve todas las reservas en las que participa un usuario,
    usando su correo → CI → reservas.
    """
    sql_ci = "SELECT ci FROM participante WHERE email = %s"
    rows_ci = execute_query(sql_ci, (correo,), fetch=True)
    if not rows_ci:
        return []

    ci = rows_ci[0]["ci"]

    query = """
        SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha, r.id_turno, r.estado
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s
        ORDER BY r.fecha DESC;
    """
    result = execute_query(query, (ci,), fetch=True)
    return cast(List[ReservaRow], result)



def cancelar_reserva_usuario(id_reserva: int, correo: str, is_admin: bool = False):
    """
    Cancela una reserva solo si:
    - El usuario participa en ella
    - La reserva está activa
    """
    sql_ci = "SELECT ci FROM participante WHERE email = %s"
    rows_ci = execute_query(sql_ci, (correo,), fetch=True)
    if not rows_ci:
        raise PermissionError("Usuario no encontrado")

    ci = rows_ci[0]["ci"]

    # Verificar que es participante
    sql_check = """
        SELECT r.estado
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE r.id_reserva = %s AND rp.ci_participante = %s;
    """
    rows = execute_query(sql_check, (id_reserva, ci), fetch=True)

    if not rows and not is_admin:
        raise PermissionError("No puedes modificar una reserva que no es tuya")

    estado = rows[0]["estado"]
    if estado != "activa":
        raise PermissionError(f"La reserva no está activa (estado={estado})")

    # Cancelar
    sql_cancel = "UPDATE reserva SET estado = 'cancelada' WHERE id_reserva = %s;"
    execute_query(sql_cancel, (id_reserva,), fetch=False)
