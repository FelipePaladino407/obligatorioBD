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

    is_admin = bool(user["isAdmin"])

    token = generate_token(correo=user["correo"], is_admin=is_admin)
    return jsonify({"token": token}), 200
