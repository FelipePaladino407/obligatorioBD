from app.models.participante_model import ParticipanteCreate
from app.db import execute_query

def create_participante(p: ParticipanteCreate):
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
