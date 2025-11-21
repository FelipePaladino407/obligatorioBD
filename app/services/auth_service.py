from typing import Any, Dict, Optional
from app.db import execute_query
import bcrypt 

def verify_user(correo: str, contrasena: str) -> Optional[Dict[str, Any]]:
    """
    Verifica si el usuario existe y si su contraseña es correcta.
    Solo para desarrollo: compara texto plano, no hashes.
    """
    query: str = """
        SELECT correo, contrasena, isAdmin 
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

    if bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8")):
        return user_row  

    return None


def cambiar_contrasena_service(correo: str, actual: str, nueva: str) -> None:
    """
    Cambia la contraseña de un usuario.
    Lógica correcta:
      - Validar que la contraseña actual coincide
      - Actualizar la nueva (ideal: hasheada)
    """

    # Traigo la contraseña actual:
    row = execute_query(
        "SELECT contrasena FROM login WHERE correo = %s",
        (correo,),
        fetch=True
    )

    if not row:
        raise Exception("Usuario no encontrado")

    hash_guardado = row[0]["contrasena"]

    # Valido contraseña actual
    contrasena_ok = (
        actual == hash_guardado or
        bcrypt.checkpw(actual.encode("utf-8"), hash_guardado.encode("utf-8"))
    )

    if not contrasena_ok:
        raise PermissionError("Contraseña actual incorrecta")

    # Hashear la nueva contraseña (como dios manda):
    hash_nuevo = bcrypt.hashpw(
        nueva.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    # 4. Guardar en la INFAME BD:
    execute_query(
        "UPDATE login SET contrasena = %s WHERE correo = %s",
        (hash_nuevo, correo),
        fetch=False
    )
