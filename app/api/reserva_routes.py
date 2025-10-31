from flask import Blueprint, jsonify, request
from app.auth import required_token
from app.models.reserva_model import ReservaCreate
from app.services.reserva_service import create_reserva, list_reservas, remove_reserva

reserva_bp = Blueprint("reserva", __name__)

@reserva_bp.get("/")
def get_reservas():
    reservas = list_reservas()
    # Convertimos todo a tipos que JSON entiende
    reservas_serializadas = [
        {
            "id": r["id_reserva"],
            "nombre_sala": r["nombre_sala"],
            "edificio": r["edificio"],
            "fecha": r["fecha"].isoformat(),  # date → string
            "id_turno": r["id_turno"],
            "estado": r["estado"]
        } for r in reservas
    ]
    print(reservas)
    return jsonify(reservas_serializadas)


@reserva_bp.post("/")
@required_token
def create():
    data = request.get_json(force=True)
    reserva = ReservaCreate(
            nombre_sala=data["nombre_sala"],
            edificio=data["edificio"],
            fecha=data["fecha"],
            id_turno=data["id_turno"],
            estado=data["estado"],
            )
    create_reserva(reserva)
    return jsonify({"message": "eguro, ahi va"}), 201

@reserva_bp.delete("/<int:id>")
@required_token
def remove(id: int):
    remove_reserva(id)
    return jsonify({"message": "Reserva eliminada"}), 200
