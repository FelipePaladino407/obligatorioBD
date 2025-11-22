from flask import request, jsonify, Blueprint

from app.auth import required_token, admin_required
from app.db import execute_query
from app.enums.extra.estado_incidencia import EstadoIncidencia
from app.enums.extra.gravedad_incidencia import GravedadIncidencia
from app.enums.extra.tipo_incidencia import TipoIncidencia

from app.models.extra.incidencia_model import IncidenciaCreate, IncidenciaUpdateEstado
from app.services.extra.alerta_reserva_service import propagar_alertas_por_incidencia
from app.services.extra.incidencia_service import crear_incidencia, listar_incidencias_por_sala, \
    actualizar_estado_incidencia

incidencia_bp = Blueprint("incidencia", __name__)

@incidencia_bp.post("/")
@required_token
def crear():
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json(force=True)

    # Buscar CI por correo
    try:
        sql_ci = "SELECT ci FROM participante WHERE email = %s LIMIT 1;"
        rows_ci = execute_query(sql_ci, (correo,), fetch=True)

        if not rows_ci:
            return jsonify({"error": "No se encontró participante para ese correo"}), 400

        ci_reportante = rows_ci[0]["ci"]

        incidencia = IncidenciaCreate(
            nombre_sala=data["nombre_sala"],
            edificio=data["edificio"],
            ci_reportante=ci_reportante,
            tipo=TipoIncidencia(data["tipo"]),
            gravedad=GravedadIncidencia(data["gravedad"]),
            descripcion=data["descripcion"],
            id_reserva=data.get("id_reserva"),
        )

        # Crear incidencia en la BD
        id_incidencia = crear_incidencia(incidencia)

        # Propagar alertas a reservas futuras según gravedad
        mensaje_base = f"Incidencia reportada: {incidencia.descripcion}"
        creadas = propagar_alertas_por_incidencia(
            id_incidencia=id_incidencia,
            nombre_sala=incidencia.nombre_sala,
            edificio=incidencia.edificio,
            gravedad=incidencia.gravedad.value,
            mensaje_base=mensaje_base,
        )

        return jsonify({
            "id_incidencia": id_incidencia,
            "alertas_creadas": creadas
        }), 201
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500

    

@incidencia_bp.get("/sala")
@admin_required
def listar_por_sala():
    try:
        nombre_sala = request.args.get("nombre_sala")
        edificio = request.args.get("edificio")
        filas = listar_incidencias_por_sala(nombre_sala, edificio)
        return jsonify(filas), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@incidencia_bp.patch("/<int:id>/estado")
@admin_required
def cambiar_estado(id: int):
    try:
        data = request.get_json(force=True)
        nuevo_estado = EstadoIncidencia(data["nuevo_estado"])
        upd = IncidenciaUpdateEstado(id_incidencia=id, nuevo_estado=nuevo_estado)
        actualizar_estado_incidencia(upd)
        return jsonify({"message": "Estado actualizado"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500
