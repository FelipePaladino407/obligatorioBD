
from __future__ import annotations
from typing import Callable, Any
from datetime import datetime, timedelta
from functools import wraps

from flask import jsonify, request
import jwt

from app.config import Config


def generate_token(correo: str, is_admin: bool) -> str:
    """
    Genera un JWT con correo e is_admin en el payload.
    """
    payload = {
        "correo": correo,
        "is_admin": bool(is_admin),
        "exp": datetime.utcnow() + timedelta(hours=2),
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

            request.correo = data.get("correo")  # USO 'correo'
            request.user_email = data.get("correo")
            request.is_admin = bool(data.get("is_admin", False))
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

# Por si acaso:  request.user_email = data.get("correo")   # esto es viejo
#             request.is_admin = bool(data.get("is_admin", False))