from typing import Any, Dict, List, cast, Optional, Tuple
from app.db import execute_query
from app.models.sala_model import SalaCreate, SalaRow, SalaUpdate

def create_sala(s: SalaCreate) -> None:
    """
    Crea una sala. Valida capacidad > 0 (por las dudas, además del CHECK en BD).
    PK compuesta: (nombre_sala, edificio).
    """
    if s.capacidad <= 0:
        raise ValueError("La capacidad debe ser mayor que 0")

    query: str = """
        INSERT INTO sala (nombre_sala, edificio, capacidad, tipo_sala)
        VALUES (%s, %s, %s, %s);
    """
    params: tuple[str, str, int, str] = (s.nombre_sala, s.edificio, s.capacidad, s.tipo_sala.value)
    execute_query(query, params, fetch=False)

def listar_salas() -> List[SalaRow]:
    query: str = "SELECT * FROM sala;"
    result: List[Dict[str, Any]] = execute_query(query, None, fetch=True)
    return cast(List[SalaRow], result)

def eliminar_sala(nombre_sala: str, edificio: str) -> None:
    """
    Borra la sala. Fallará si hay reservas que referencian esa sala (FK).
    """
    query: str = "DELETE FROM sala WHERE nombre_sala=%s AND edificio=%s;"
    params: tuple[str, str] = (nombre_sala, edificio)
    execute_query(query, params, fetch=False)

def update_sala(update: SalaUpdate) -> None:
    """
    Actualiza solo los campos provistos (SET parcial).
    Se identifica por clave compuesta (nombre_sala, edificio).
    """
    sets: List[str] = []
    params: List[Any] = []

    if update.capacidad is not None:
        if update.capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que 0")
        sets.append("capacidad = %s")
        params.append(update.capacidad)

    if update.tipo_sala is not None:
        sets.append("tipo_sala = %s")
        params.append(update.tipo_sala)

    if not sets:
        return

    query: str = f"UPDATE sala SET {', '.join(sets)} WHERE nombre_sala=%s AND edificio=%s;"
    params.extend([update.nombre_sala, update.edificio])
    execute_query(query, tuple(params), fetch=False)
