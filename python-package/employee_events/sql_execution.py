"""Database access for the employee_events package.

Each query opens a connection, runs the SQL, closes the connection and
returns the result.
"""
from contextlib import closing
from functools import wraps
from pathlib import Path
from sqlite3 import connect

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "employee_events.db"


class SQLExecutionMixin:
    """Adds methods for running SQL against employee_events.db."""

    def query(self, sql, params=()):
        """Run a query and return the rows as a list of tuples."""
        # closing() makes sure the connection is closed even on error
        with closing(connect(DB_PATH)) as connection:
            cursor = connection.execute(sql, params)
            return cursor.fetchall()

    def pandas_query(self, sql, params=()):
        """Run a query and return the result as a DataFrame."""
        with closing(connect(DB_PATH)) as connection:
            return pd.read_sql_query(sql, connection, params=params)


def query_decorator(func):
    """Run the SQL string returned by `func` and return the rows."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        sql = func(*args, **kwargs)
        with closing(connect(DB_PATH)) as connection:
            return connection.execute(sql).fetchall()

    return wrapper
