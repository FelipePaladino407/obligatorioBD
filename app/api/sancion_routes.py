from typing import List
from flask import Blueprint, jsonify, request

from app.auth import required_token, admin_required
from app.models.sancion_model import SancionCreate
from app.services.sancion_service import (
    crear_sancion,
    listar_sanciones,
    listar_sanciones_por_correo,
)
from datetime import date

sancion_bp = Blueprint("sancion", __name__)

@sancion_bp.get("/")
def list():
    try:
        sanciones = listar_sanciones()
        return jsonify(sanciones)
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@sancion_bp.post("/")
@admin_required
def create():
    data = request.get_json(force=True)
    sancion = SancionCreate(
        ci_participante=data["ci_participante"],
        fecha_inicio=data["fecha_inicio"],
        fecha_fin=data["fecha_fin"],
        motivo=data["motivo"],
    )
    try:
        crear_sancion(sancion)
        return jsonify({"message": "Muchacho fletado"}), 201
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


@sancion_bp.get("/me")
@required_token
def mis_sanciones():
    """
    Devuelve las sanciones del usuario logueado.
    """
    correo = getattr(request, "correo", None)
    if not correo:
        return jsonify({"error": "No se pudo obtener el correo del token"}), 401

    try:
        rows = listar_sanciones_por_correo(correo)
    except Exception as e:
        return jsonify({"error": f"Error consultando BD: {e}"}), 500

    hoy = date.today()
    sanciones = []
    for row in rows:
        sanciones.append(
            {
                "ci": row["ci_participante"],
                "fecha_inicio": row["fecha_inicio"].isoformat(),
                "fecha_fin": row["fecha_fin"].isoformat(),
                "motivo": row["motivo"],
                "activa": hoy >= row["fecha_inicio"] and hoy <= row["fecha_fin"],
            }
        )

    return jsonify(
        {
            "correo": correo,
            "total": len(sanciones),
            "sanciones": sanciones,
        }
    ), 200
