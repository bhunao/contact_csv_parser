from pathlib import Path

from fastapi.testclient import TestClient


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


def test_persons_table_template(client: TestClient) -> None:
    response = client.get(
        "/persons/all",
    )
    assert response.status_code == 200
    assert response.template is not None
    assert response.template.name == "persons_table.html"
