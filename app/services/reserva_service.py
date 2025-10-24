from datetime import date
from typing import Dict, List, cast
from app.db import execute_query
from app.models.participante_model import ParticipanteRow
from app.models.reserva_model import ReservaCreate, ReservaRow, ReservaUpdate
from app.enums.estado_reserva import EstadoReserva


def create_reserva(r: ReservaCreate) -> None:
    """
    Crea una reserva, claramente
    Args:
        r (ReservaCreate): Modelo de reserva
    """
    query: str = """
    INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado) 
    VALUES
    (%s, %s, %s, %s, %s);
    """
    params: tuple[str, str, date, int, str] = (r.nombre_sala, r.edificio, r.fecha, r.id_turno, r.estado.value)
    execute_query(query, params, fetch=False)

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
