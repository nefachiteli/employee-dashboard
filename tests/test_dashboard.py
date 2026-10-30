import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "report"))

import dashboard  # noqa: E402


@pytest.fixture(scope="module")
def client():
    return TestClient(dashboard.app)


@pytest.mark.parametrize("url", ["/", "/employee/4", "/team/2"])
def test_pages_render_with_charts_and_notes(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert response.text.count("data:image/png;base64") == 2
    assert "Manager notes" in response.text


@pytest.mark.parametrize("url", ["/employee/9999", "/employee/abc", "/team/77"])
def test_unknown_ids_return_404(client, url):
    assert client.get(url).status_code == 404


def test_dropdown_switches_between_employees_and_teams(client):
    teams = client.get("/update_dropdown?profile_type=Team").text
    assert "Alpha Team" in teams
    people = client.get("/update_dropdown?profile_type=Employee").text
    assert "Alex Martinez" in people


def test_update_data_redirects_to_selected_page(client):
    response = client.post(
        "/update_data",
        data={"profile_type": "Team", "user_selection": "3"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/team/3"
