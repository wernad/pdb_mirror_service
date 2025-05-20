"""Tests for file-related endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch

from app.main import app
from app.api.dependencies import get_file_service, get_protein_service

client = TestClient(
    app, base_url="http://testserver/api/v1/files", raise_server_exceptions=False
)

# Mock data
MOCK_PROTEIN_ID = "1abc"
MOCK_PROTEIN_FULL_ID = "pdb_00001abc"
MOCK_VERSION = 1
MOCK_DATE = datetime(2024, 1, 1)
MOCK_BINARY_FILE_CONTENT = b"\x00"
MOCK_FILE_CONTENT = "\x00"


@pytest.fixture(autouse=True)
def cleanup_dependencies():
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_file_service():
    """Fixture for mocking file service."""
    with patch("app.api.dependencies.get_file_service") as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        yield mock_service


@pytest.fixture
def mock_protein_service():
    """Fixture for mocking protein service."""
    with patch("app.api.dependencies.get_protein_service") as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        yield mock_service


def test_ping():
    """Test the ping endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200


def test_get_latest_cif_success(mock_file_service):
    """Test successful retrieval of latest CIF file."""
    mock_file_service.get_latest_by_protein_id.return_value = MOCK_BINARY_FILE_CONTENT

    response = client.get(f"/{MOCK_PROTEIN_ID}/latest")
    assert response.status_code == 200
    assert response.content == MOCK_BINARY_FILE_CONTENT
    assert (
        response.headers["Content-Disposition"]
        == f'attachment; filename="pdb_mirror_{MOCK_PROTEIN_FULL_ID}.cif"'
    )


def test_get_latest_cif_not_found(mock_file_service):
    """Test getting latest CIF when file doesn't exist."""
    mock_file_service.get_latest_by_protein_id.return_value = None

    def get_file_service_override():
        return mock_file_service

    app.dependency_overrides[get_file_service] = get_file_service_override

    response = client.get(f"/{MOCK_PROTEIN_ID}/latest")

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"File entry for protein '{MOCK_PROTEIN_FULL_ID}' not found."
    }


def test_get_cif_at_version_success(mock_file_service):
    """Test successful retrieval of CIF file at specific version."""
    mock_file_service.get_by_version_and_protein_id.return_value = MOCK_FILE_CONTENT

    response = client.get(f"/{MOCK_PROTEIN_ID}/version/{MOCK_VERSION}")
    assert response.status_code == 200
    assert response.text == MOCK_FILE_CONTENT
    assert (
        response.headers["Content-Disposition"]
        == f'attachment; filename="pdb_mirror_{MOCK_PROTEIN_FULL_ID}_v{MOCK_VERSION}.cif"'
    )


def test_get_cif_at_version_not_found(mock_file_service):
    """Test getting CIF at version when file doesn't exist."""
    mock_file_service.get_by_version_and_protein_id.return_value = None

    def get_file_service_override():
        return mock_file_service

    app.dependency_overrides[get_file_service] = get_file_service_override

    response = client.get(f"/{MOCK_PROTEIN_ID}/version/{MOCK_VERSION}")
    assert response.status_code == 404


def test_get_latest_cif_prior_success(mock_file_service):
    """Test successful retrieval of latest CIF file prior to date."""
    mock_file_service.get_latest_by_id_before_date.return_value = MOCK_FILE_CONTENT

    response = client.get(f"/{MOCK_PROTEIN_ID}/date/{MOCK_DATE.isoformat()}")
    assert response.status_code == 200
    assert response.text == MOCK_FILE_CONTENT
    assert (
        response.headers["Content-Disposition"]
        == f'attachment; filename="pdb_mirror_{MOCK_PROTEIN_FULL_ID}_{MOCK_DATE}.cif"'
    )


def test_get_latest_cif_prior_not_found(mock_file_service):
    """Test getting latest CIF prior to date when file doesn't exist."""

    def get_file_service_override():
        mock_file_service.get_latest_by_id_before_date.return_value = None
        return mock_file_service

    app.dependency_overrides[get_file_service] = get_file_service_override

    response = client.get(f"/{MOCK_PROTEIN_ID}/date/{MOCK_DATE.isoformat()}")
    assert response.status_code == 404


def test_get_new_cif_files_success(mock_protein_service):
    """Test successful retrieval of new CIF files after date."""
    mock_ids = ["1ABC", "2DEF"]
    mock_protein_service.get_protein_ids_after_date.return_value = mock_ids

    def get_protein_service_override():
        return mock_protein_service

    app.dependency_overrides[get_protein_service] = get_protein_service_override
    response = client.get(f"/date/{MOCK_DATE.isoformat()}")

    assert response.status_code == 200
    assert response.json() == mock_ids


# def test_get_new_cif_files_not_found(mock_protein_service):
#     """Test getting new CIF files when none exist after date."""
#     mock_protein_service.get_protein_ids_after_date.return_value = []

#     response = client.get(f"/date/{MOCK_DATE.isoformat()}")
#     assert response.status_code == 404
