from typing import Any, Dict, List, cast
from app.db import execute_query
from app.models.edificio_model import EdificioRow

def listar_edificios() -> List[EdificioRow]:
    """
    Obtiene la tabla 'edificio' de la base del dato
    Args:
        None
    Returns:
        Despues te digo
    """
    query: str = """
    SELECT * FROM edificio;
    """

    result: List[Dict] = execute_query(query, None, fetch=True)
    return cast(List[EdificioRow], result) 


