from typing import Any, Dict, List, cast, Optional, Tuple
from app.db import execute_query
from app.models.sala_model import SalaCreate, SalaRow, SalaUpdate, SalaEstadoRow, EstadoOperativo
from app.enums.tipo_sala import TipoSala

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
    execute_query(query, params, fetch=False, is_admin=True) # TIENE QUE SER ADMIN

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
    execute_query(query, params, fetch=False, is_admin=True)

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
    execute_query(query, tuple(params), fetch=False, is_admin=True)
    
    
    
def get_tipo_sala(nombre_sala: str, edificio: str) -> TipoSala:
    query: str = "SELECT tipo_sala FROM sala WHERE nombre_sala=%s AND edificio=%s;"
    params: tuple[str, str] = (nombre_sala, edificio) 
    result = execute_query(query, params, fetch=True)
    return cast(TipoSala, result[0]['tipo_sala'])


def get_sala(nombre_sala: str, edificio: str) -> Optional[SalaRow]:
    """
    Obtiene una sala por su clave primaria compuesta (nombre_sala, edificio).
    Devuelve un SalaRow o None si no existe.
    """
    query = """
        SELECT * 
        FROM sala
        WHERE nombre_sala = %s AND edificio = %s;
    """
    params = (nombre_sala, edificio)

    result: List[Dict[str, Any]] = execute_query(query, params, fetch=True)

    if not result:
        return None

    return cast(SalaRow, result[0])


# +++ NUEVO: leer estado (VIEW → fallback)
def obtener_estado_sala(nombre_sala: str, edificio: str) -> Optional[SalaEstadoRow]:
    """
    Intenta leer 'vista_estado_sala' (estado_calculado + estado_manual).
    Si no existe la VIEW, cae a la columna 'estado' de la tabla 'sala'
    y la usa como calculado y manual.
    """
    # 1) Intentar VIEW
    try:
        sql_view = """
            SELECT nombre_sala, edificio, estado_calculado, estado_manual
            FROM vista_estado_sala
            WHERE nombre_sala=%s AND edificio=%s;
        """
        rows = execute_query(sql_view, (nombre_sala, edificio), fetch=True)
        if rows:
            return cast(SalaEstadoRow, rows[0])
    except Exception:
        pass

    # 2) Fallback tabla 'sala'
    sql_tbl = """
        SELECT nombre_sala, edificio, estado AS estado_manual
        FROM sala
        WHERE nombre_sala=%s AND edificio=%s;
    """
    rows2 = execute_query(sql_tbl, (nombre_sala, edificio), fetch=True)
    if not rows2:
        return None
    out = cast(SalaEstadoRow, rows2[0])
    out["estado_calculado"] = out["estado_manual"]
    return out


# +++ NUEVO: listar todas con estado (VIEW → fallback)
def listar_salas_con_estado() -> List[SalaEstadoRow]:
    try:
        sql_view = """
            SELECT nombre_sala, edificio, estado_calculado, estado_manual
            FROM vista_estado_sala
            ORDER BY edificio, nombre_sala;
        """
        rows = execute_query(sql_view, None, fetch=True)
        return cast(List[SalaEstadoRow], rows)
    except Exception:
        sql_tbl = """
            SELECT nombre_sala, edificio, estado AS estado_manual
            FROM sala
            ORDER BY edificio, nombre_sala;
        """
        rows = execute_query(sql_tbl, None, fetch=True)
        for r in rows:
            r["estado_calculado"] = r["estado_manual"]
        return cast(List[SalaEstadoRow], rows)


# +++ NUEVO: actualizar estado manual (admin)
def actualizar_estado_manual(nombre_sala: str, edificio: str, nuevo_estado: EstadoOperativo) -> None:
    sql = "UPDATE sala SET estado=%s WHERE nombre_sala=%s AND edificio=%s;"
    execute_query(sql, (nuevo_estado, nombre_sala, edificio), fetch=False, is_admin=True)


# +++ NUEVO: helper para bloquear reservas si está fuera de servicio
def sala_disponible_para_reserva(nombre_sala: str, edificio: str) -> bool:
    est = obtener_estado_sala(nombre_sala, edificio)
    if not est:
        return False
    return est["estado_calculado"] != "fuera_de_servicio"
