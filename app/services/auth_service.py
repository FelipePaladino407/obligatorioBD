from typing import Any, Dict, Optional
from app.db import execute_query
import bcrypt 

def verify_user(correo: str, contrasena: str) -> Optional[Dict[str, Any]]:
    """
    Verifica si el usuario existe y si su contraseña es correcta.
    Solo para desarrollo: compara texto plano, no hashes.
    """
    query: str = """
        SELECT correo, contrasena 
        FROM login 
        WHERE correo = %s;
    """
    params: tuple[str, ...] = (correo,)
    result = execute_query(query, params, True)

    if not result:
        return None  

    user_row = result[0]
    hash_guardado: str = user_row["contrasena"]

    if contrasena == hash_guardado:
        return user_row  

    if bcrypn.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8")):
        return user_row  

    return None
