"""Testing the API endpoints and the templates returned by Jinja"""
import pytest
from pathlib import Path

from fastapi.testclient import TestClient


NEED_DIFF_DB = "Precisa de algo tipo um 'mock'."


def test_upload_valid_csv(client: TestClient) -> None:
    file = Path("app/tests/data/valid_csv.csv")
    file_content = file.read_text()

    files = {
        "file": (
            "test_file.csv",
            file_content,
            "text/plain"
        )}
    response = client.post(
        "/persons/upload_csv",
        files=files
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "alert.html"
    assert response.context["alert_type"] == "success"


def test_upload_invalid_csv(client: TestClient):
    file = Path("app/tests/data/invalid_csv.csv")
    file_content = file.read_text()

    files = {
        "file": (
            "test_file.csv",
            file_content,
            "text/plain"
        )}
    response = client.post(
        "/persons/upload_csv",
        files=files
    )
    assert response.status_code == 400
    assert response.template is not None
    assert response.template.name == "alert.html"
    assert response.context["alert_type"] == "danger"


def test_index_template(client: TestClient) -> None:
    response = client.get(
        "/persons/",
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "index.html"


@pytest.mark.skip(NEED_DIFF_DB)
def test_get_valid_person_data_template(client: TestClient) -> None:
    valid_id = "TOTALLY_VALID_ID"
    response = client.get(
        f"/persons/data/{valid_id}",
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "person_data.html"
    assert response.context["person"].id == valid_id


def test_get_invalid_person_data_template(client: TestClient) -> None:
    invalid_id = "TOTALLY_VALID_ID"
    response = client.get(
        f"/persons/data/{invalid_id}",
    )
    assert response.status_code == 404
    assert response.template is not None
    assert response.template.name == "person_data.html"
    assert response.context["error"] == "Person id not found."


@pytest.mark.skip(NEED_DIFF_DB)
def test_edit_valid_person_data_template(client: TestClient) -> None:
    valid_id = "TOTALLY_VALID_ID"
    response = client.get(
        f"/persons/data/{valid_id}/edit",
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "person_data.html"
    assert response.context["person"].id == valid_id


def test_edit_invalid_person_data_template(client: TestClient) -> None:
    invalid_id = "TOTALLY_VALID_ID"
    response = client.get(
        f"/persons/data/{invalid_id}/edit",
    )
    assert response.status_code == 404
    assert response.template is not None
    assert response.template.name == "person_data.html"
    assert response.context["error"] == "Person id not found."


def test_persons_table_template(client: TestClient) -> None:
    response = client.get(
        "/persons/all",
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "persons_table.html"


def test_persons_changelog_table_template(client: TestClient) -> None:
    response = client.get(
        "/persons/changelog",
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "changes_table.html"
