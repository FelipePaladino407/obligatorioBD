
from typing import List
from flask import Blueprint, jsonify, request

from app.auth import required_token
from app.models.sancion_model import SancionCreate
from app.services.sancion_service import crear_sancion, listar_sanciones


sancion_bp = Blueprint("sancion", __name__)

@sancion_bp.get("/")
def list():
    sanciones = listar_sanciones()
    return jsonify(sanciones)

@sancion_bp.post("/")
@required_token
def create():
    data = request.get_json(force=True)
    sancion = SancionCreate(
           ci_participante=data["ci_participante"],
           fecha_inicio=data["fecha_inicio"],
           fecha_fin=data["fecha_fin"],
           motivo=data["motivo"]
            )
    crear_sancion(sancion)
    return jsonify({"message": "Muchacho fletado"}), 201
