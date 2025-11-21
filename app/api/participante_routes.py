from app.auth import required_token, admin_required
from app.db import execute_query
from app.models.participante_model import ParticipanteCreate, ParticipanteRow, ParticipanteUpdate
from app.services.participante_service import (
    create_participante,
    eliminar_participante,
    listar_participantes,
    update_participante,
    obtener_datos_participante_por_correo,
)
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
        # 1) crear participante
        create_participante(participante)

        # 2) crear login
        sql_login = """
            INSERT INTO login (correo, contrasena, isAdmin)
            VALUES (%s, %s, false);
        """
        execute_query(sql_login, (participante.email, data["password"]), fetch=False)

        return jsonify({"message": "Participante + login creados"}), 201

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
    correo = getattr(request, "correo", None)

    if not correo:
        return jsonify({"error": "No se pudo obtener el correo del token"}), 401

    try:
        row = obtener_datos_participante_por_correo(correo)
    except Exception as e:
        return jsonify({"error": f"Error consultando BD: {e}"}), 500

    if not row:
        return jsonify({"error": "Participante no encontrado"}), 404

    return jsonify({
        "ci": row["ci"],
        "nombre": row["nombre"],
        "apellido": row["apellido"],
        "email": row["email"],
        "carrera": row.get("carrera"),
        "tipo_programa": row.get("tipo_programa"),
        "rol": row.get("rol"),
        "facultad": row.get("facultad"),
        "is_admin": bool(getattr(request, "is_admin", False)),
    }), 200



