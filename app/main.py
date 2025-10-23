from ast import Tuple
from typing import Any, List
from mysql.connector import cursor
from mysql.connector.cursor import MySQLCursor
from app.models.participante_model import ParticipanteCreate
from app.services.participante_service import create_participante, eliminar_participante, listar_participantes
from app.db import execute_query 


"""
EJEMPLO
"""
def main():
    query: str = "SELECT nombre_sala, edificio, estado FROM reserva WHERE estado = %s;"
    params : tuple[str] = ("activa",)
    result = execute_query(query, params, True)

    print("Cantidad de ratas atrapadas en el subsuelo del Mullin desde 2016: 446\n")
    print("Reservas activas")
    for row in result:
        print(f"Nombre: {row['nombre_sala']}, Edificio: {row['edificio']}, Estado: {row['estado']}")
    partete = ParticipanteCreate(
            ci="54701087",
            nombre="Pedro",
            apellido="Navaja",
            email="pedro.navaja@ucu.edu.uy"
            )

    # create_participante(partete)
    # eliminar_participante(partete.ci)
    resultete = listar_participantes()
    for row in resultete: 
        print(f"CI: {row['ci']}, Nombre: {row['nombre']}, Apellido: {row['apellido']}, Email: {row['email']}")

if __name__ == "__main__":
    main()
