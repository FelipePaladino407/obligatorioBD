# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from app.auth import generate_token, required_token, revocar_sesion  # aniado lo del toquen requerido y lo de revocar secion.
import bcrypt

from app.db import execute_query
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


@auth_bp.post("/logout")
@required_token
def logout():
    """
    Cierra la *sesión actual* (no todas).
    Usa el session_id que viene del token.
    """
    sesion_id = getattr(request, "session_id", None)
    if not sesion_id:
        return jsonify({"error": "No se pudo determinar la sesión"}), 400

    try:
        revocar_sesion(sesion_id)
    except Exception as e:
        return jsonify({"error": f"No se pudo cerrar sesión: {e}"}), 500

    return jsonify({"message": "Logout exitoso"}), 200


@auth_bp.patch("/cambiar_contrasena")
@required_token
def cambiar_contrasena():
    data = request.get_json(force=True)
    actual = data.get("contrasena_actual")
    nueva = data.get("nueva_contrasena")

    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No se pudo obtener el usuario"}), 401

    # buscar contraseña existente
    sql_get = "SELECT contrasena FROM login WHERE correo = %s"
    row = execute_query(sql_get, (correo,), fetch=True)

    if not row or row[0]["contrasena"] != actual:
        return jsonify({"error": "Contraseña actual incorrecta"}), 403

    sql_update = "UPDATE login SET contrasena = %s WHERE correo = %s"
    execute_query(sql_update, (nueva, correo), fetch=False)

    return jsonify({"message": "Contraseña actualizada correctamente"}), 200
