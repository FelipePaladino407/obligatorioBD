from ast import Tuple
from typing import Any, Dict, List, Optional, Union
import mysql.connector
from mysql.connector import Error, MySQLConnection
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.errors import DatabaseError
from mysql.connector.pooling import PooledMySQLConnection
from app.config import Config

# Metemos un tipo compuesto (interesante)
MySQLConn = Union[PooledMySQLConnection, MySQLConnectionAbstract]

def get_connection() -> MySQLConn:
    """
    Crea una conexión con la base de datos (obtengo variables globales del Config)
    Args:
        None
    Returns:
        MySQLConn: La conexión en cuestión
    """
    try:
        conn: MySQLConn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                database=Config.DB_NAME
                )

        return conn
    except Error as e:
        raise DatabaseError(f"Error de conexion a MySQL: {e}") from e

def execute_query(query: str, params: Optional[tuple[Any, ...]], fetch: bool) -> List[Dict[str, Any]]:
    """
    Realiza una consulta a la base de datos SQL (eguro)

    Args:
        query (str): La query SQL a ejecutar
        params (tuple[Any, ...]): Parametros para la query
        fetch (bool): si se deben retornar los resultados

    Returns:
        List[Dict[str, Any]]: lista de resultados de la consulta (devuelve [] si fetch = false)
    """
    connection: MySQLConn = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        result : List[Dict[str, Any]] = cursor.fetchall() 
        if not fetch:
            result = []
        connection.commit()
        return result
    except Error as e:
        connection.rollback()
        print(f"Error ejecutando query: {e}")
        raise e
    finally:
        cursor.close()
        connection.close()
        

