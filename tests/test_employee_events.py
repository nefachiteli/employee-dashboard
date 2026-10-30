from contextlib import closing
from pathlib import Path
from sqlite3 import connect

import pytest

project_root = Path(__file__).resolve().parent.parent

TABLE_QUERY = "SELECT name FROM sqlite_master WHERE type = 'table'"


@pytest.fixture
def db_path():
    return project_root / "python-package" / "employee_events" / "employee_events.db"


def test_db_exists(db_path):
    assert db_path.is_file()


def test_employee_table_exists(db_path):
    with closing(connect(db_path)) as connection:
        tables = [row[0] for row in connection.execute(TABLE_QUERY)]
    assert "employee" in tables


def test_team_table_exists(db_path):
    with closing(connect(db_path)) as connection:
        tables = [row[0] for row in connection.execute(TABLE_QUERY)]
    assert "team" in tables


def test_employee_events_table_exists(db_path):
    with closing(connect(db_path)) as connection:
        tables = [row[0] for row in connection.execute(TABLE_QUERY)]
    assert "employee_events" in tables
