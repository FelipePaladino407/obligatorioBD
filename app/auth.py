
from __future__ import annotations
from typing import Callable, Any
from datetime import datetime, timedelta
from functools import wraps
# PARA EL LOGOUT
import uuid

from flask import jsonify, request
import jwt

from app.config import Config
from app.db import execute_query # Nuevo


def generate_token(correo: str, is_admin: bool) -> str:
    """
    Genera un JWT con correo, is_admin y un session_id (UUID) en el payload.
    También registra la sesión en BD.
    """
    exp_dt = datetime.utcnow() + timedelta(hours=2)

    # OPCIONAL: si querés permitir solo una sesión activa por usuario,
    # podés revocar todas las anteriores acá:
    # execute_query("UPDATE sesion_login SET revocado = TRUE WHERE correo=%s;", (correo,), fetch=False)

    sesion_id = _crear_sesion_en_bd(correo, exp_dt)

    payload = {
        "sid": sesion_id,              # <--- session_id (UUID)
        "correo": correo,
        "is_admin": bool(is_admin),
        "exp": exp_dt,
        "iat": datetime.utcnow()
    }
    token: str = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return token



def required_token(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Falta token"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

            correo = data.get("correo")
            sesion_id = data.get("sid")

            if not correo or not sesion_id:
                return jsonify({"error": "Token sin sesión"}), 401

            # Validar la sesión en BD:
            if not _sesion_valida(sesion_id, correo):
                return jsonify({"error": "Sesión inválida o cerrada"}), 401

            # Guardamos cosas útiles en request
            request.correo = correo
            request.user_email = correo
            request.is_admin = bool(data.get("is_admin", False))
            request.session_id = sesion_id

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token vencido"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        except Exception:
            return jsonify({"error": "Error verificando token"}), 401

        return func(*args, **kwargs)
    return wrapper



def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Exige:
    - Token válido
    - Que el usuario sea admin (is_admin = True)
    """
    @wraps(func)
    @required_token
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not getattr(request, "is_admin", False):
            return jsonify({"error": "quien sos"}), 403
        return func(*args, **kwargs)
    return wrapper


def _crear_sesion_en_bd(correo: str, exp_dt: datetime) -> str:
    """
    Crea un registro de sesión y devuelve su UUID (string).
    """
    sesion_id = str(uuid.uuid4())

    # convierto a str para que el blackMan no se queje:
    exp_str = exp_dt.strftime("%Y-%m-%d %H:%M:%S")

    sql = """
        INSERT INTO sesion_login (id, correo, expiracion)
        VALUES (%s, %s, %s);
    """
    params = (sesion_id, correo, exp_str)
    execute_query(sql, params, fetch=False)
    return sesion_id


def _sesion_valida(sesion_id: str, correo: str) -> bool:
    """
    Chequea en BD que la sesión exista, no esté revocada y no esté vencida.
    """
    sql = """
        SELECT revocado, expiracion
        FROM sesion_login
        WHERE id = %s AND correo = %s;
    """
    rows = execute_query(sql, (sesion_id, correo), fetch=True)
    if not rows:
        return False

    row = rows[0]
    if row["revocado"]:
        return False

    exp_bd: datetime = row["expiracion"]
    # Por si las moscas, comparo contra UTC actual.
    return datetime.utcnow() <= exp_bd


def revocar_sesion(sesion_id: str) -> None:
    sql = "UPDATE sesion_login SET revocado = TRUE WHERE id = %s;"
    execute_query(sql, (sesion_id,), fetch=False)



# Por si acaso:  request.user_email = data.get("correo")   # esto es viejo
#             request.is_admin = bool(data.get("is_admin", False))