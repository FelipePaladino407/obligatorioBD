from app.auth import required_token, admin_required
from app.db import execute_query
from app.models.participante_model import ParticipanteCreate, ParticipanteRow, ParticipanteUpdate, ParticpanteProgramaUpdate
from app.services.participante_service import (
    create_participante,
    eliminar_participante,
    listar_participantes,
    update_participante,
    obtener_datos_participante_por_correo,
    update_particpante_programa,
)
from flask import Blueprint, jsonify, request


participante_bp = Blueprint("participante", __name__)

@participante_bp.get("/")
def listar():
    try:
        participantes = listar_participantes()
        return jsonify(participantes), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


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
        execute_query(sql_login, (participante.email, data["password"]), fetch=False, is_admin=True)

                # 3) crear participante_programa_academico
        sql_part_prog = """
            INSERT INTO participante_programa_academico (ci_participante, nombre_programa, rol)
            VALUES (%s, %s, %s);
        """
        execute_query(
            sql_part_prog,
            (participante.ci, data["nombre_programa"], data["rol"]),
            fetch=False,
            is_admin=True
        )

        return jsonify({"message": "Participante + login + programa creados"}), 201

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

    participante_data = data.get("participante", {})
    participante_update = ParticipanteUpdate(
        ci=ci,
        nombre=participante_data.get("nombre"),
        apellido=participante_data.get("apellido"),
        email=participante_data.get("email"),
    )

    # Datos del programa académico (MODIFICACION DE ULTIMO MOMENTO) EMERGENCIA
    # No funca lo de modificar cedula. Rompe integridad referencial
    programa_data = data.get("programa", {})

    participante_programa_update = ParticpanteProgramaUpdate(
        ci=ci,
        nombre_programa=programa_data.get("nombre_programa"),
        rol=programa_data.get("rol")
    )

    try:
        if any([
            participante_update.nombre is not None,
            participante_update.apellido is not None,
            participante_update.email is not None
        ]):
            update_participante(participante_update)

        if any([
            participante_programa_update.nombre_programa is not None,
            participante_programa_update.rol is not None,
        ]):
            update_particpante_programa(participante_programa_update)

        return jsonify({"message": "Participante actualizado joya"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


@participante_bp.patch("/me")
@required_token
def actualizar_mis_datos():
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No se pudo obtener usuario del token"}), 401

    data = request.get_json(force=True)

    # Solo permitimos cambiar datos personales
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")

    # validar email si se quiere actualizar
    if email is not None and not email.strip():
        return jsonify({"error": "El email no puede estar vacío"}), 400

    try:
        # Obtener CI real del usuario (no lo recibimos por payload)
        row = obtener_datos_participante_por_correo(correo)
        if not row:
            return jsonify({"error": "Participante no encontrado"}), 404

        ci = row["ci"]

        participante_update = ParticipanteUpdate(
            ci=ci,
            nombre=nombre,
            apellido=apellido,
            email=email,
        )

        # Si no se envió nada actualizable
        if all([nombre is None, apellido is None, email is None]):
            return jsonify({"message": "No se enviaron cambios"}), 200

        update_participante(participante_update)

        return jsonify({"message": "Perfil actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# POR FAVOR NO VEAS ESTO  
from app.db import execute_query

def _validar_usuario_tiene_reserva(ci: str, id_reserva: int, nombre_sala: str, edificio: str) -> bool:
    sql = """
        SELECT 1
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE r.id_reserva = %s
          AND r.nombre_sala = %s
          AND r.edificio = %s
          AND r.estado = 'activa'
          AND rp.ci_participante = %s
        LIMIT 1;
    """
    rows = execute_query(sql, (id_reserva, nombre_sala, edificio, ci), fetch=True)
    return bool(rows)




