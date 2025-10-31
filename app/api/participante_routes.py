from app.auth import required_token
from app.models.participante_model import ParticipanteCreate, ParticipanteRow, ParticipanteUpdate
from app.services.participante_service import create_participante, eliminar_participante, listar_participantes, update_participante
from flask import Blueprint, jsonify, request

participante_bp = Blueprint("participante", __name__)

@participante_bp.get("/")
def listar():
    participantes = listar_participantes()
    return jsonify(participantes)

@participante_bp.post("/")
@required_token
def crear():
    data = request.get_json(force=True)
    participante = ParticipanteCreate(
        ci=data["ci"],
        nombre=data["nombre"],
        apellido=data["apellido"],
        email=data["email"],
    )
    create_participante(participante)
    return jsonify({"message": "Participante creado"}), 201


@participante_bp.delete("/<string:ci>")
@required_token
def eliminar(ci: str):
    eliminar_participante(ci)
    return jsonify({"message": "Participante eliminado"}), 200




@participante_bp.patch("/<string:ci>")
@required_token
def actualizar(ci: str):
    data = request.get_json(force=True)
    participante_update = ParticipanteUpdate(
        ci=ci,
        nombre=data.get("nombre"),
        apellido=data.get("apellido"),
        email=data.get("email"),
    )
    update_participante(participante_update)
    return jsonify({"message": "Participante actualizado correctamente"}), 200

