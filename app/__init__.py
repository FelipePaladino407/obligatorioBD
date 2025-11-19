from flask import Flask
from flask_cors import CORS
from app.api.auth_routes import auth_bp
from app.api.participante_routes import participante_bp
from app.api.reserva_routes import reserva_bp
from app.api.sancion_routes import sancion_bp
from app.api.reportes_routes import reportes_bp
from app.api.sala_routes import sala_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(participante_bp, url_prefix="/api/v1/participante")
    app.register_blueprint(reserva_bp, url_prefix="/api/v1/reserva")
    app.register_blueprint(sancion_bp, url_prefix="/api/v1/sancion")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(sala_bp, url_prefix="/api/v1/sala")
    app.register_blueprint(reportes_bp, url_prefix="/api/v1/reportes")
    return app
