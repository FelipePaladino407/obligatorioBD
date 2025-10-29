
from __future__ import annotations
from typing import Callable, Any
from datetime import datetime, timedelta
from functools import wraps

from flask import jsonify, request
import jwt

from app.config import Config


def generate_token(id_usuario: int) -> str:
    """
    Genera un JWT con id_usuario en el payload. Eguro.
    """
    payload = {
        "id_usuario": id_usuario,
        "exp": datetime.utcnow() + timedelta(hours=2),
        "iat": datetime.utcnow()
    }
    token: str = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return token


def required_token(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador de interiores que exige un token Bearer válido en Authorization header.
    Si el token es válido, agrega request.id_usuario y ejecuta la func.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        token: str | None = None
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Te faltó el token, flaco"}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

            request.id_usuario = data.get("id_usuario")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token vencido"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inberbe"}), 401
        except Exception as e:
            return jsonify({"error": "Error verificando token"}), 401

        # OJALDRE: llamar a la función original y devolver su resultado
        return func(*args, **kwargs)
    return wrapper

