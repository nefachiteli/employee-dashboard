import pytest

from employee_events import Employee, Team


@pytest.mark.parametrize("model, expected", [(Employee(), 25), (Team(), 5)])
def test_names_lists_every_row(model, expected):
    assert len(model.names()) == expected


def test_username_returns_full_name():
    assert Employee().username(4) == [("Daniela Rivera",)]
    assert Team().username(2) == [("Bravo Team",)]


def test_unknown_id_has_no_username():
    assert Employee().username(9999) == []


@pytest.mark.parametrize("model, entity_id", [(Employee(), 4), (Team(), 2)])
def test_event_counts_columns_and_order(model, entity_id):
    df = model.event_counts(entity_id)
    assert list(df.columns) == ["event_date", "positive_events", "negative_events"]
    assert df["event_date"].is_monotonic_increasing


def test_team_model_data_has_one_row_per_employee():
    assert len(Team().model_data(2)) == 6


def test_employee_model_data_is_one_row():
    assert len(Employee().model_data(4)) == 1


def test_notes_have_date_and_text():
    df = Employee().notes(4)
    assert list(df.columns) == ["note_date", "note"]
    assert len(df) > 0
