"""Pytest configuration file."""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)


@pytest.fixture(autouse=True)
def mock_db_engine():
    """Mock database engine for all tests."""
    with patch("app.database.database.engine") as mock_engine:
        yield mock_engine


@pytest.fixture(autouse=True)
def mock_db_session(mock_db_engine):
    """Mock database session for all tests."""
    with patch("app.database.database.get_session") as mock:
        mock_session = Mock()
        mock.return_value = mock_session
        yield mock_session
