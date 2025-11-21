from typing import Any, Dict, List, Optional, cast
from app.enums import tipo_usuario
from app.models.participante_model import ParticipanteCreate, ParticipanteRow, ParticipanteUpdate
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
    query: str = """
    SELECT p.ci, p.nombre, p.apellido, p.email, pp.nombre_programa, pp.rol, pa.tipo 
    FROM participante p JOIN participante_programa_academico pp on p.ci = pp.ci_participante JOIN reservas_salas_estudio.programa_academico pa on pp.nombre_programa = pa.nombre_programa
    """

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

def update_participante(update: ParticipanteUpdate) -> None:
    """
    Actualiza un participeta recibiendo un objeto donde se actualizan los atributos distintos de None
    Args:
        update (ParticipanteUpdate): Modelo de participante
    """
    query: str = "UPDATE participante SET "
    params = []
    updates = []

    if update.nombre is not None:
        updates.append("nombre = %s")
        params.append(update.nombre)
    if update.email is not None:
        updates.append("email = %s")
        params.append(update.email)
    if update.apellido is not None:
        updates.append("apellido = %s")
        params.append(update.apellido)

    if not updates:
        return

    query += ", ".join(updates) + "WHERE ci = %s"
    params.append(update.ci)
    execute_query(query, tuple(params), fetch=False)

def get_participante_rol(ci: str) -> tipo_usuario.TipoUsuario:
    query: str = """
    SELECT rol FROM participante_programa_academico WHERE ci_participante = %s; 
    """
    params: tuple[str] = (ci, );
    rol: List[Dict[str, Any]] = execute_query(query, params, fetch=True);
    return cast(tipo_usuario.TipoUsuario, rol[0]["rol"])

# Agrego para obtener los datos del usuario (Para: FrontEnd BlackMan)
def obtener_datos_participante_por_correo(correo: str) -> Optional[Dict[str, Any]]:
    """
    Devuelve los datos del participante (mis datos) a partir del correo.
    Incluye programa, facultad y rol si existe esa info.
    """
    sql = """
        SELECT 
            p.ci,
            p.nombre,
            p.apellido,
            p.email,
            pa.nombre_programa      AS carrera,
            pa.tipo                 AS tipo_programa,   -- 'grado' / 'posgrado'
            ppa.rol,                                   -- 'estudiante_grado', 'docente', etc.
            f.nombre               AS facultad
        FROM participante p
        LEFT JOIN participante_programa_academico ppa
            ON p.ci = ppa.ci_participante
        LEFT JOIN programa_academico pa
            ON pa.nombre_programa = ppa.nombre_programa
        LEFT JOIN facultad f
            ON f.id_facultad = pa.id_facultad
        WHERE p.email = %s
        LIMIT 1;
    """
    rows = execute_query(sql, (correo,), fetch=True)
    if not rows:
        return None
    return rows[0]
