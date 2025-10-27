from datetime import date
from typing import Any, Dict, List, Optional, cast
from app.db import execute_query
from app.models.sancion_model import SancionCreate, SancionOut, SancionRow

def crear_sancion(s: SancionCreate) -> None:
    """
    Crea una sanción. La BD ya tiene CHECK (fecha_fin > fecha_inicio),
    pero valido tambien del lado de la app para posible error temprano.
    """
    if s.fecha_fin <= s.fecha_inicio:
        raise ValueError("La fecha_fin debe ser posterior a fecha_inicio")

    query: str = """
        INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin, motivo)
        VALUES (%s, %s, %s, %s);
    """
    params: tuple[str, date, date, str] = (s.ci_participante, s.fecha_inicio, s.fecha_fin, s.motivo)
    execute_query(query, params, fetch=False)

def eliminar_sancion(ci: str, fecha_inicio: date) -> None:
    """
    Elimina una sanción puntual por PK compuesta (ci_participante, fecha_inicio).
    """
    query: str = "DELETE FROM sancion_participante WHERE ci_participante=%s AND fecha_inicio=%s;"
    params: tuple[str, date] = (ci, fecha_inicio)
    execute_query(query, params, fetch=False)

def listar_sanciones() -> List[SancionRow]:
    query: str = "SELECT ci_participante, fecha_inicio, fecha_fin, motivo FROM sancion_participante;"
    result: List[Dict[str, Any]] = execute_query(query, None, fetch=True)
    return cast(List[SancionRow], result)

def listar_sanciones_por_participante(ci: str) -> List[SancionRow]:
    query: str = """
        SELECT ci_participante, fecha_inicio, fecha_fin, motivo
        FROM sancion_participante
        WHERE ci_participante=%s
        ORDER BY fecha_inicio DESC;
    """
    result: List[Dict[str, Any]] = execute_query(query, (ci,), fetch=True)
    return cast(List[SancionRow], result)

def tiene_sancion_activa(ci: str, en_fecha: date) -> bool:
    """
    Devuelve True si 'en_fecha' pertenece a [fecha_inicio, fecha_fin] para el CI dado.
    """
    query: str = """
        SELECT 1
        FROM sancion_participante
        WHERE ci_participante=%s AND %s BETWEEN fecha_inicio AND fecha_fin
        LIMIT 1;
    """
    rows: List[Dict] = execute_query(query, (ci, en_fecha), fetch=True)
    return len(rows) > 0
