"""Service module for managing change tracking operations.

This module provides a service layer for handling change tracking operations,
including recording and managing changes to protein entries.
"""

from sqlmodel import Session
from app.database.repositories import ChangeRepository

from app.database.models import ChangeInsert


class ChangeService:
    """Service class for managing change tracking operations.

    This class provides methods for recording and managing changes to protein entries,
    including bulk operations for tracking multiple changes.
    """

    change_repository: ChangeRepository

    def __init__(self, db: Session):
        """Initialize the change service with database session.

        Args:
            db: SQLModel database session.
        """
        self.change_repository = ChangeRepository(db)

    def insert_bulk_added(self, entries: list[ChangeInsert]):
        """Inserts information about protein entry changes.

        Args:
            List of change records to insert.
        """
        values = []
        for entry in entries:
            values.append(
                {
                    "protein_id": entry.protein_id,
                    "operation_flag": entry.operation_flag,
                    "timestamp": entry.timestamp,
                }
            )

        self.change_repository.insert_bulk(entries)
