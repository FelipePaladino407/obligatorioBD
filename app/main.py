from ast import Tuple
from typing import Any, List
from mysql.connector import cursor
from mysql.connector.cursor import MySQLCursor
from db import execute_query 


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

if __name__ == "__main__":
    main()
