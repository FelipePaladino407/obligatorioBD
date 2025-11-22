from flask import Blueprint, jsonify, request
from app.auth import admin_required, required_token
from app.db import execute_query
from app.models.sala_model import SalaCreate, SalaUpdate
from app.enums.tipo_sala import TipoSala
from app.services.sala_service import (
    create_sala,
    listar_salas,
    listar_salas_con_estado,
    get_sala,
    update_sala,
    eliminar_sala,
    actualizar_estado_manual, obtener_estado_sala
)

sala_bp = Blueprint("salas", __name__)

VALID_ESTADOS_SALA = {"operativa", "con_inconvenientes", "fuera_de_servicio"}

@sala_bp.get("/")
def listar():
    try:
        salas = listar_salas()
        return jsonify(salas), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500

@sala_bp.post("/")
@admin_required
def crear():
    data = request.get_json(force=True)

    sala = SalaCreate(
        nombre_sala=data["nombre_sala"],
        edificio=data["edificio"],
        capacidad=data["capacidad"],
        tipo_sala=TipoSala(data["tipo_sala"])
    )
    try:
        create_sala(sala)
        return jsonify({"message": "Sala creada joya"}), 201
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@sala_bp.get("/<string:nombre_sala>/<string:edificio>")
def obtener(nombre_sala: str, edificio: str):
    sala = get_sala(nombre_sala, edificio)
    if not sala:
        return jsonify({"message": "Sala no encontrada"}), 404
    return jsonify(sala)

@sala_bp.patch("/")
@admin_required
def actualizar():
    try:
        data = request.get_json(force=True)

        if "nombre_sala" not in data or "edificio" not in data:
            return jsonify({"message": "Faltan identificadores: nombre_sala y edificio"}), 400
        
        nombre_sala = data["nombre_sala"]
        edificio = data["edificio"]
        
        tipo_sala_enum = None
        if "tipo_sala" in data:
            try:
                tipo_sala_enum = TipoSala(data["tipo_sala"])
            except ValueError:
                 return jsonify({"error": f"Tipo de sala inválido: {data['tipo_sala']}"}), 400

        sala_update = SalaUpdate(
            nombre_sala=nombre_sala,
            edificio=edificio,
            capacidad=data.get("capacidad"),
            tipo_sala=tipo_sala_enum
        )
        update_sala(sala_update)
        return jsonify({"message": "Sala actualizada correctamente"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error al actualizar la sala"}), 500

@sala_bp.delete("/")
@admin_required
def eliminar():
    data = request.get_json(force=True)

    if "nombre_sala" not in data or "edificio" not in data:
        return jsonify({"message": "Faltan ids: nombre_sala y edificio"}), 400

    nombre_sala = data["nombre_sala"]
    edificio = data["edificio"]

    try:
        eliminar_sala(nombre_sala, edificio)
        return jsonify({"message": "Sala incinerada"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@sala_bp.patch("/estado_manual/<string:nombre>/<string:edificio>")
@admin_required
def actualizar_estado_manual_route(nombre: str, edificio: str):
    data = request.get_json(force=True)
    nuevo_estado = data.get("estado")

    if nuevo_estado not in VALID_ESTADOS_SALA:
        return jsonify({
            "error": "Estado inválido. Debe ser 'operativa', 'con_inconvenientes' o 'fuera_de_servicio'"
        }), 400

    try:
        actualizar_estado_manual(nombre, edificio, nuevo_estado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Estado manual actualizado correctamente",
        "sala": nombre,
        "edificio": edificio,
        "estado_manual": nuevo_estado
    }), 200


@sala_bp.get("/estado")
@required_token
def listar_estado_salas():
    result = listar_salas_con_estado()
    return jsonify(result), 200


@sala_bp.get("/estado/<string:nombre>/<string:edificio>")
@required_token
def estado_sala_especifica(nombre, edificio):
    result = obtener_estado_sala(nombre, edificio)
    if not result:
        return jsonify({"error": "Sala no encontrada"}), 404
    return jsonify(result), 200