from flask import request, jsonify, Blueprint

from app.api.participante_routes import _validar_usuario_tiene_reserva
from app.auth import required_token, admin_required
from app.db import execute_query
from app.enums.extra.estado_incidencia import EstadoIncidencia
from app.enums.extra.gravedad_incidencia import GravedadIncidencia
from app.enums.extra.tipo_incidencia import TipoIncidencia

from app.models.extra.incidencia_model import IncidenciaCreate, IncidenciaUpdateEstado
from app.services.extra.alerta_reserva_service import propagar_alertas_por_incidencia
from app.services.extra.incidencia_service import crear_incidencia, listar_incidencias_por_sala, \
    actualizar_estado_incidencia, listar_incidencias_por_reportante
from app.services.participante_service import obtener_datos_participante_por_correo

incidencia_bp = Blueprint("incidencia", __name__)

@incidencia_bp.post("/")
@required_token
def crear():
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json(force=True)

    participante = obtener_datos_participante_por_correo(correo)
    if not participante:
        return jsonify({"error": "No se encontró participante para ese correo"}), 400

    ci_reportante = participante["ci"]

    id_reserva = data.get("id_reserva")
    if not id_reserva:
        return jsonify({
            "error": "Debe indicar la reserva desde la que se reporta la incidencia (id_reserva)."
        }), 400

    nombre_sala = data.get("nombre_sala")
    edificio = data.get("edificio")

    # Valido que el energumeno tenga esa reserva activa en esa sala:
    tiene_reserva = _validar_usuario_tiene_reserva(
        ci_reportante,
        id_reserva,
        nombre_sala,
        edificio
    )

    if not tiene_reserva:
        return jsonify({
            "error": "No tenés una reserva activa sobre esa sala, no podés reportar una incidencia."
        }), 403

    try:
        incidencia = IncidenciaCreate(
            nombre_sala=nombre_sala,
            edificio=edificio,
            ci_reportante=ci_reportante,
            tipo=TipoIncidencia(data["tipo"]),
            gravedad=GravedadIncidencia(data["gravedad"]),
            descripcion=data["descripcion"],
            id_reserva=id_reserva,
        )
    except Exception as e:
        return jsonify({"error": f"Datos inválidos: {str(e)}"}), 400

    id_incidencia = crear_incidencia(incidencia)

    mensaje_base = f"Incidencia reportada: {incidencia.descripcion}"
    alertas_creadas = propagar_alertas_por_incidencia(
        id_incidencia=id_incidencia,
        nombre_sala=incidencia.nombre_sala,
        edificio=incidencia.edificio,
        gravedad=incidencia.gravedad.value,
        mensaje_base=mensaje_base,
    )

    return jsonify({
        "id_incidencia": id_incidencia,
        "alertas_creadas": alertas_creadas
    }), 201


@incidencia_bp.get("/sala")
@admin_required
def listar_por_sala():
    nombre_sala = request.args.get("nombre_sala")
    edificio = request.args.get("edificio")
    filas = listar_incidencias_por_sala(nombre_sala, edificio)
    return jsonify(filas), 200


@incidencia_bp.patch("/<int:id>/estado")
@admin_required
def cambiar_estado(id: int):
    data = request.get_json(force=True)
    nuevo_estado = EstadoIncidencia(data["nuevo_estado"])
    upd = IncidenciaUpdateEstado(id_incidencia=id, nuevo_estado=nuevo_estado)
    actualizar_estado_incidencia(upd)
    return jsonify({"message": "Estado actualizado"}), 200

@incidencia_bp.get("/me")
@required_token
def mis_incidencias():
    """
    Devuelve todas las incidencias reportadas por el usuario logueado.
    Se obtiene el CI a partir del correo del token.
    """
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No autenticado"}), 401

    participante = obtener_datos_participante_por_correo(correo)
    if not participante:
        return jsonify({"error": "No se encontró participante para ese correo"}), 400

    ci = participante["ci"]

    incidencias = listar_incidencias_por_reportante(ci)

    return jsonify(incidencias), 200