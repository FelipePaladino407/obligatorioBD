from flask import Flask
from flask_cors import CORS

from app.api.alerta_reserva_routes import alerta_bp
from app.api.auth_routes import auth_bp
from app.api.incidencia_routes import incidencia_bp
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
    app.register_blueprint(incidencia_bp, url_prefix="/api/v1/incidencia")
    app.register_blueprint(alerta_bp, url_prefix="/api/v1/alerta")
    return app