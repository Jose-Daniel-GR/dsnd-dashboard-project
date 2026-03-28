from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

#Absolute path to the database
db_path = Path(__file__).parent / "employee_events.db"

# MIXIN for handling SQLite connections
class QueryMixin:
    """
    Mixin que maneja conexion SQLite.
    Abre conexion, ejecuta SQL, cierra y retorna datos.
    """

    def pandas_query(self, sql_query: str) -> pd.DataFrame:
        """Ejecuta SQL y retorna un DataFrame de pandas."""
        connection = connect(db_path)
        try:
            result = pd.read_sql_query(sql_query, connection)
        finally:
            connection.close()
        return result

    def query(self, sql_query: str) -> list:
        """Ejecuta SQL y retorna lista de tuplas."""
        connection = connect(db_path)
        try:
            cursor = connection.cursor()
            result = cursor.execute(sql_query).fetchall()
        finally:
            connection.close()
        return result


# Alternative decorator
def query(func):
    """
    Decorator que ejecuta SQL y retorna
    lista de tuplas.
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query