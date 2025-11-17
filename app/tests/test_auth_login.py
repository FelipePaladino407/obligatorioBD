# app/tests/test_auth_login.py
from app.auth import generate_token

def test_login_returns_token(client, monkeypatch):
    # Mockear verify_user para no tocar la DB
    def fake_verify_user(correo, contrasena):
        if correo == "marrarteChelo@ucu.edu.uy" and contrasena == "1234":
            return {"correo": correo, "contrasena": contrasena}
        return None

    monkeypatch.setattr("app.api.auth_routes.verify_user", fake_verify_user)

    resp = client.post(
        "/api/v1/auth/login",
        json={"correo": "marrarteChelo@ucu.edu.uy", "contrasena": "1234"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data and isinstance(data["token"], str) and len(data["token"]) > 10
