# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from app.auth import generate_token
import bcrypt
from app.services.auth_service import verify_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
def login():
    data = request.get_json(force=True)
    correo = data.get("correo")
    contrasena = data.get("contrasena")

    user = verify_user(correo, contrasena)
    if not user:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = generate_token(id_usuario=user["correo"])
    return jsonify({"token": token}), 200

