from ast import Tuple
from typing import Any, Dict, List, Optional, Union
import mysql.connector
from mysql.connector import Error, MySQLConnection
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.errors import DatabaseError
from mysql.connector.pooling import PooledMySQLConnection
from app.config import Config
from app.validators.validator import validate_params

# Metemos un tipo compuesto (interesante)
MySQLConn = Union[PooledMySQLConnection, MySQLConnectionAbstract]

def get_connection(is_admin: bool) -> MySQLConn:
    """
    Crea una conexión usando credenciales de admin o de app_user.
    """
    try:
        user = Config.DB_USER_ADMIN if is_admin else Config.DB_USER_APP
        password = Config.DB_PASS_ADMIN if is_admin else Config.DB_PASS_APP

        conn: MySQLConn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=user,
            password=password,
            database=Config.DB_NAME
        )
        return conn

    except Error as e:
        raise DatabaseError(f"Error de conexión a MySQL ({'admin' if is_admin else 'app_user'}): {e}") from e


def execute_query( query: str, params: Optional[tuple[Any, ...]], fetch: bool, is_admin: bool = False) -> List[Dict[str, Any]]:
    """
    Ejecuta una query usando credenciales según is_admin.
    UUU
    """
    validate_params(params)

    connection: MySQLConn = get_connection(is_admin=is_admin)
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        result: List[Dict[str, Any]] = cursor.fetchall() if fetch else []
        connection.commit()
        return result

    except Error as e:
        connection.rollback()
        print(f"Error ejecutando query: {e}")
        raise e

    finally:
        cursor.close()
        connection.close()



def execute_returning_id(query: str, params: Optional[tuple[Any, ...]] = None, is_admin: bool = False) -> int:
    conn = get_connection(is_admin=is_admin)
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute(query, params or ())
        last_id = cur.lastrowid or 0
        conn.commit()
        return last_id

    except Error as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()

