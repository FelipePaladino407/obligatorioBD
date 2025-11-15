from datetime import date
from re import error
from typing import Dict, List, cast
from app.db import execute_query, execute_returning_id
from app.enums.tipo_sala import TipoSala
from app.enums.tipo_usuario import TipoUsuario
from app.models.participante_model import ParticipanteRow
from app.models.reserva_model import ReservaCreate, ReservaRow, ReservaUpdate
from app.enums.estado_reserva import EstadoReserva
from app.services.participante_service import get_participante_rol
from app.services.sala_service import get_sala, get_tipo_sala


def create_reserva(r: ReservaCreate) -> None:
    # crea la reserva y obtener el id generado (muy importante)
    query_reserva = """
    INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado)
    VALUES (%s, %s, %s, %s, %s);
    """
    params_reserva = (
        r.nombre_sala,
        r.edificio,
        r.fecha,
        r.id_turno,
        r.estado.value,
    )

    validar_capacidad(r)
    validar_participantes_rol_sala(r)
    # OJO -> FALTA: 
    # 4. Validar límites (solo grado):
    #       - máximo 2 horas por día
    #       - máximo 3 reservas activas por semana
    # 5. Si todo OK -> insertar reserva
    # 6. Insertar reserva_participante para cada CI

    id_reserva = execute_returning_id(query_reserva, params_reserva)

    query_participante = """
    INSERT INTO reserva_participante (ci_participante, id_reserva, asistencia)
    VALUES (%s, %s, %s);
    """

    for ci in r.participantes_ci:
        params_participante = (ci, id_reserva, False)
        execute_query(query_participante, params_participante, fetch=False)


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
    execute_query(query, params, fetch=False)

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

# def validar_cantidad_reservas(r: ReservaCreate):
#     raise error("pa")
