# app/tests/test_reportes_endpoint.py
from app.auth import generate_token

def _auth_header():
    # Cualquier id_usuario sirve; el decorador valida firma/exp.
    return {"Authorization": f"Bearer {generate_token(1)}"}

def test_reportes_salas_mas_reservadas_ok(client, monkeypatch):
    fake_rows = [
        {"nombre_sala": "Sala 3", "edificio": "Mullin", "reservas": 2},
        {"nombre_sala": "Sala 2", "edificio": "El central", "reservas": 1},
    ]

    def fake_execute_query(sql, params, fetch):
        return fake_rows

    # 👈 mock sobre la referencia importada en el módulo del modelo
    monkeypatch.setattr("app.models.reportes_model.execute_query", fake_execute_query)

    resp = client.get(
        "/v1/reportes?id_consulta=SALAS_MAS_RESERVADAS&limit=5",
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["columns"] == ["nombre_sala", "edificio", "reservas"]
    assert data["rows"][0] == ["Sala 3", "Mullin", 2]


def test_reportes_requires_token(client):
    # Sin header Authorization → 401/403 según tu decorador
    resp = client.get("/v1/reportes?id_consulta=SALAS_MAS_RESERVADAS")
    assert resp.status_code in (401, 403)
