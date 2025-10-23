from typing import Any, Dict, List, cast
from app.models.participante_model import ParticipanteCreate, ParticipanteRow
from app.db import execute_query

def create_participante(p: ParticipanteCreate) -> None:
    """
    Da de alta a un participante en el sistema
    Args:
        p (ParticipanteCreate): datos del participante en cuestión

    """
    query: str = """
        INSERT INTO participante (ci, nombre, apellido, email)
        VALUES (%s, %s, %s, %s);
    """
    params: tuple[str, str, str, str] = (p.ci, p.nombre, p.apellido, p.email)
    execute_query(query, params, fetch=False)


def listar_participantes() -> List[ParticipanteRow]:
    """
    Obtiene la tabla 'participante' de la base del dato
    Args:
        None
    Returns:
        Despues te digo
    """
    query: str = "SELECT * FROM participante;"
    result: List[Dict[str, Any]] = execute_query(query, None, fetch=True)
    return cast(List[ParticipanteRow], result) 

def eliminar_participante(ci: str) -> None:
    """
    Elimina un participante de la base del dato
    Args:
        ci (str): ci del participante
    """
    query: str = "DELETE FROM participante WHERE ci = %s;"
    params: tuple[str] = (ci,) 
    execute_query(query, params, fetch=False)
