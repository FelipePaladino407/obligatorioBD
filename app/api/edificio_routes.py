# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify

from app.auth import required_token
from app.services.edificio_service import listar_edificios

edificio_bp = Blueprint("edificio", __name__)

@edificio_bp.get("/")
@required_token
def get_edificios():
    try:
        edificios = listar_edificios()
        return jsonify(edificios), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


