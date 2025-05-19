"""Base repository module for database operations.

This module provides a base repository class that all other repositories inherit from,
establishing a common interface for database operations.
"""

from sqlmodel import Session


class RepositoryBase:
    """Base repository class for database operations.

    This class provides a common interface for all repositories, handling
    database session management and basic CRUD operations.

    Args:
        db: The database session to use for operations.
    """

    def __init__(self, db: Session):
        self.db = db
