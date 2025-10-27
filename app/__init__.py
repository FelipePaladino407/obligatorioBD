from flask import Flask
from app.api.participante_routes import participante_bp
from app.api.reserva_routes import reserva_bp
from app.api.sancion_routes import sancion_bp

def create_app() -> Flask:
    app = Flask(__name__)
    # Registrar los famosos Blueprints
    app.register_blueprint(participante_bp, url_prefix="/api/v1/participante")
    app.register_blueprint(reserva_bp, url_prefix="/api/v1/reserva")
    app.register_blueprint(sancion_bp, url_prefix="/api/v1/sancion")
    return app
