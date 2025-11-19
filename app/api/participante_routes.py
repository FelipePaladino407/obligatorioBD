from app.auth import required_token, admin_required
from app.models.participante_model import ParticipanteCreate, ParticipanteRow, ParticipanteUpdate
from app.services.participante_service import create_participante, eliminar_participante, listar_participantes, update_participante, obtener_datos_participante_por_correo
from flask import Blueprint, jsonify, request

participante_bp = Blueprint("participante", __name__)

@participante_bp.get("/")
def listar():
    participantes = listar_participantes()
    return jsonify(participantes)

@participante_bp.post("/")
@admin_required
def crear():
    data = request.get_json(force=True)
    participante = ParticipanteCreate(
        ci=data["ci"],
        nombre=data["nombre"],
        apellido=data["apellido"],
        email=data["email"],
    )
    try:
        create_participante(participante)
        return jsonify({"message": "Participante creado"}), 201
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@participante_bp.delete("/<string:ci>")
@admin_required
def eliminar(ci: str):
    try:
        eliminar_participante(ci)
        return jsonify({"message": "Participante eliminado"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@participante_bp.patch("/<string:ci>")
@admin_required
def actualizar(ci: str):
    data = request.get_json(force=True)
    participante_update = ParticipanteUpdate(
        ci=ci,
        nombre=data.get("nombre"),
        apellido=data.get("apellido"),
        email=data.get("email"),
    )
    try:
        update_participante(participante_update)
        return jsonify({"message": "Participante actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500

# Para FronTend BlackMan:
@participante_bp.get("/me")
@required_token
def mis_datos():
    """
    Devuelve los datos del usuario logueado, usando el correo del JWT.
    """
    correo = getattr(request, "id_usuario", None)
    if not correo:
        return jsonify({"error": "No se pudo determinar el usuario a partir del token"}), 401

    row = obtener_datos_participante_por_correo(correo)
    if not row:
        return jsonify({"error": "Participante no encontrado"}), 404

    payload = {
        "ci": row["ci"],
        "nombre": row["nombre"],
        "apellido": row["apellido"],
        "email": row["email"],
        "carrera": row.get("carrera"),
        "tipo_programa": row.get("tipo_programa"),   # grado / posgrado
        "rol": row.get("rol"),                      # estudiante_grado / docente / etc
        "facultad": row.get("facultad"),
    }
    return jsonify(payload), 200
