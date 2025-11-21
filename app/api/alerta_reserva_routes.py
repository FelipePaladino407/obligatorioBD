from flask import Blueprint, jsonify, request

from app.auth import required_token
from app.services.alerta_reserva_service import listar_alertas_usuario
from app.services.extra.alerta_reserva_service import listar_alertas_de_reserva, marcar_alerta_leida

alerta_bp = Blueprint("alerta", __name__)

@alerta_bp.get("/reserva/<int:id_reserva>")
@required_token
def alertas_reserva(id_reserva: int):
    # opcional: validar que el usuario sea admin o participe en esa reserva
    filas = listar_alertas_de_reserva(id_reserva, solo_no_leidas=False)
    return jsonify(filas), 200


@alerta_bp.patch("/<int:id_alerta>/leida")
@required_token
def marcar_leida(id_alerta: int):
    marcar_alerta_leida(id_alerta)
    return jsonify({"message": "Alerta marcada como leída"}), 200


@alerta_bp.get("/me")
@required_token
def alertas_usuario():
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No autenticado"}), 401

    result = listar_alertas_usuario(correo)
    return jsonify(result), 200