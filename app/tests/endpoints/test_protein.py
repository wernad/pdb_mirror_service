"""Tests for protein-related endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch

from app.main import app
from app.database.models import Operations
from app.api.dependencies import get_protein_service

client = TestClient(app, base_url="http://testserver/api/v1/proteins")

# Mock data
MOCK_DATE = datetime(2024, 1, 1)
MOCK_TOTAL_COUNT = 100
MOCK_IDS = ["1ABC", "2DEF", "3GHI"]
MOCK_PAGINATION = {"limit": 10, "offset": 0}


@pytest.fixture
def mock_protein_service(mock_db_session):
    """Fixture for mocking protein service."""
    with patch("app.api.dependencies.get_protein_service") as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        yield mock_service


def test_get_total_count_success(mock_protein_service):
    """Test successful retrieval of total protein count."""
    mock_protein_service.get_total_count.return_value = MOCK_TOTAL_COUNT

    def get_protein_service_override():
        return mock_protein_service

    app.dependency_overrides[get_protein_service] = get_protein_service_override

    response = client.get("/total_count")
    assert response.status_code == 200
    assert response.json() == {"total_count": MOCK_TOTAL_COUNT}


def test_get_all_ids_success(mock_protein_service):
    """Test successful retrieval of all protein IDs with pagination."""
    mock_protein_service.get_all_ids.return_value = MOCK_IDS
    mock_protein_service.get_total_count.return_value = MOCK_TOTAL_COUNT

    def get_protein_service_override():
        return mock_protein_service

    app.dependency_overrides[get_protein_service] = get_protein_service_override

    response = client.get("/all", params=MOCK_PAGINATION)
    assert response.status_code == 200
    assert response.json() == {"data": MOCK_IDS, "total_count": MOCK_TOTAL_COUNT}


def test_get_added_after_date_success(mock_protein_service):
    """Test successful retrieval of added protein IDs after date."""
    mock_protein_service.get_changes_after_date.return_value = MOCK_IDS

    def get_protein_service_override():
        return mock_protein_service

    app.dependency_overrides[get_protein_service] = get_protein_service_override

    response = client.get(f"/changes/added/{MOCK_DATE.isoformat()}")
    assert response.status_code == 200
    assert response.json() == MOCK_IDS

    mock_protein_service.get_changes_after_date.assert_called_once_with(
        start_date=MOCK_DATE, change=Operations.ADDED
    )


def test_get_modified_after_date_success(mock_protein_service):
    """Test successful retrieval of modified protein IDs after date."""
    mock_protein_service.get_changes_after_date.return_value = MOCK_IDS

    def get_protein_service_override():
        return mock_protein_service

    app.dependency_overrides[get_protein_service] = get_protein_service_override

    response = client.get(f"/changes/modified/{MOCK_DATE.isoformat()}")
    assert response.status_code == 200
    assert response.json() == MOCK_IDS

    mock_protein_service.get_changes_after_date.assert_called_once_with(
        start_date=MOCK_DATE, change=Operations.MODIFIED
    )


def test_get_removed_after_date_success(mock_protein_service):
    """Test successful retrieval of removed protein IDs after date."""
    mock_protein_service.get_changes_after_date.return_value = MOCK_IDS

    def get_protein_service_override():
        return mock_protein_service

    app.dependency_overrides[get_protein_service] = get_protein_service_override

    response = client.get(f"/changes/obsolete/{MOCK_DATE.isoformat()}")
    assert response.status_code == 200
    assert response.json() == MOCK_IDS

    mock_protein_service.get_changes_after_date.assert_called_once_with(
        start_date=MOCK_DATE, change=Operations.OBSOLETE
    )
