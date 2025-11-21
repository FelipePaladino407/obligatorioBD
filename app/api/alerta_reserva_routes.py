from flask import Blueprint, jsonify

from app.auth import required_token
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
