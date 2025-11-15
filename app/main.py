from app import create_app
from app.services.participante_service import get_participante_rol
from app.services.sala_service import get_tipo_sala

app = create_app()

if __name__ == "__main__":
    # app.run(debug=True)
    print(get_participante_rol('54055666'))
    print(get_tipo_sala('Sala 3', 'Mullin'))


# from ast import Tuple
# from typing import Any, List
# from mysql.connector import cursor
# from mysql.connector.cursor import MySQLCursor
# from app.models.participante_model import ParticipanteCreate
# from app.services.participante_service import create_participante, eliminar_participante, listar_participantes
# from app.db import execute_query
# from app.services.reserva_service import update_reserva 
#
#
# """
# EJEMPLO
# """
# def main():
#     query: str = "SELECT nombre_sala, edificio, estado FROM reserva WHERE estado = %s;"
#     params : tuple[str] = ("activa",)
#     result = execute_query(query, params, True)
#
#     print("Cantidad de ratas atrapadas en el subsuelo del Mullin desde 2016: 446\n")
#     print("Reservas activas")
#     for row in result:
#         print(f"Nombre: {row['nombre_sala']}, Edificio: {row['edificio']}, Estado: {row['estado']}")
#     partete = ParticipanteCreate(
#             ci="49995071",
#             nombre="Maybeth",
#             apellido="Garcés",
#             email="mayFilosofa123@ucu.edu.uy"
#             )
#
#     # Verifico si ya existe el participante antes de insertarlo
#     existe = execute_query(
#         "SELECT 1 FROM participante WHERE ci = %s OR email = %s;",
#         (partete.ci, partete.email),
#         fetch=True
#     )
#
#     if existe:
#         print(f"\n⚠️ El participante {partete.nombre} {partete.apellido} ya existe, no se puede insertar nuevamente\n.")
#     else:
#         create_participante(partete)
#         print(f"\n✅ Participante {partete.nombre} {partete.apellido} insertado correctamente.")
#
#     # --- Mostrar todos los participantes ---
#     print("\nParticipantes en el sistema:")
#     resultete = listar_participantes()
#     for row in resultete:
#         print(f"CI: {row['ci']}, Nombre: {row['nombre']}, Apellido: {row['apellido']}, Email: {row['email']}")
#
#
# if __name__ == "__main__":
#     main()
