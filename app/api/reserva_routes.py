from flask import Blueprint, jsonify, request
from app.auth import required_token, admin_required
from app.models.reserva_model import ReservaCreate
from app.services.reserva_service import create_reserva, list_reservas, remove_reserva, list_reservas_usuario, \
    cancelar_reserva_usuario

reserva_bp = Blueprint("reserva", __name__)

@reserva_bp.get("/")
@required_token
def get_reservas():
    try:
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
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@reserva_bp.post("/")
@required_token
def create():
    data = request.get_json(force=True) or {}

    # Validar que vengan todas las claves necesarias
    required_fields = ["nombre_sala", "edificio", "fecha", "id_turno", "participantes_ci"]
    missing = [f for f in required_fields if f not in data]

    if missing:
        return jsonify({
            "error": f"Faltan campos obligatorios en el body: {', '.join(missing)}"
        }), 400

    force = data.get("force", False)

    reserva = ReservaCreate(
        nombre_sala=data["nombre_sala"],
        edificio=data["edificio"],
        fecha=data["fecha"],
        id_turno=data["id_turno"],
        estado="activa",
        participantes_ci=data["participantes_ci"]
    )

    try:
        id_res = create_reserva(reserva, force)
        return jsonify({"message": "Reserva creada", "id_reserva": id_res}), 201

    except Warning as w:
        return jsonify(w.args[0]), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@reserva_bp.delete("/<int:id>")
@admin_required
def remove(id: int):
    try:
        remove_reserva(id)
        return jsonify({"message": "Reserva eliminada por admin"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@reserva_bp.get("/mias")
@required_token
def mis_reservas():
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No se pudo obtener usuario del token"}), 401

    try:
        reservas = list_reservas_usuario(correo)
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500

    # Serializar
    reservas_serializadas = [
        {
            "id_reserva": r["id_reserva"],
            "nombre_sala": r["nombre_sala"],
            "edificio": r["edificio"],
            "fecha": r["fecha"].isoformat(),
            "id_turno": r["id_turno"],
            "estado": r["estado"],
        }
        for r in reservas
    ]

    return jsonify({"reservas": reservas_serializadas}), 200


@reserva_bp.patch("/<int:id>/cancelar")
@required_token
def cancelar_mia(id: int):
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No se pudo obtener usuario del token"}), 401

    try:
        cancelar_reserva_usuario(id, correo)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Reserva cancelada correctamente"}), 200
