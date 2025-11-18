from typing import TypedDict, Optional, cast
from flask import Blueprint, jsonify, request
from app.auth import required_token
from app.services.reportes_service import ejecutar_consulta, ConsultaID

reportes_bp = Blueprint("reportes", __name__)

class ReporteParams(TypedDict, total=False):
    desde: str
    hasta: str
    edificio: str
    facultad: str
    limit: int
    offset: int

@reportes_bp.get("/v1/reportes")
@required_token
def get_reportes():
    id_consulta: str = request.args.get("id_consulta", "").strip()
    params: ReporteParams = {
        "desde": request.args.get("desde"),
        "hasta": request.args.get("hasta"),
        "edificio": request.args.get("edificio"),
        "facultad": request.args.get("facultad"),
    }
    try:
        params["limit"] = int(request.args.get("limit", "50"))
        params["offset"] = int(request.args.get("offset", "0"))
    except ValueError:
        return jsonify({"error": "limit/offset inválidos"}), 400

    try:
        # NO: ejecutar_consulta(ConsultaID(id_consulta), params)
        payload = ejecutar_consulta(cast(ConsultaID, id_consulta), params)
        return jsonify(payload), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        # para ver el error exacto en los tetst:
        # return jsonify({"error": "Error interno", "detail": str(e)}), 500
        return jsonify({"error": "Error interno ejecutando la consulta"}), 500