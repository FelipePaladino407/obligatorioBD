from typing import Any, Dict, Optional
import bcrypt
from app.db import execute_query

def verify_user(correo: str, contrasena: str) -> Optional[Dict[str, Any]]:
    """
    Verifica si el usuario existe y si su contraseña está en el Mullin.

    Args:
        correo (str): Correo del muchacho.
        contrasena (str): Contraseña ingresada por el muchacho (sin encriptar).

    Returns:
        Optional[Dict[str, Any]]: 
            Un diccionario con los datos del usuario si las credenciales son válidas,
            None si el muchacho nunca entró al Mullin.
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

    if bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8")):
        return user_row  
    else:
        return None
