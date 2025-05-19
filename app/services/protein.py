"""Service module for managing protein data operations.

This module provides a service layer for handling protein-related operations,
including CRUD operations, bulk inserts, and change tracking.
"""

from datetime import datetime

from sqlmodel import Session
from app.database.repositories import ProteinRepository, ChangeRepository

from app.log import log as log
from app.database.models.operation_flag import Operations


class ProteinService:
    """Service class for managing protein data operations.

    This class provides methods for interacting with protein data in the database,
    including retrieving protein information, tracking changes, and bulk operations.
    """

    protein_repository: ProteinRepository
    change_repository: ChangeRepository

    def __init__(self, db: Session):
        """Initialize the protein service with database session.

        Args:
            db: SQLModel database session.
        """
        self.protein_repository = ProteinRepository(db)
        self.change_repository = ChangeRepository(db)

    def get_total_count(self) -> int:
        """Returns total number of protein entries.

        Returns:
            Total count of protein entries in the database.
        """
        count = self.protein_repository.get_total_count()

        return count

    def get_all_ids(self, limit: int, offset: int) -> list[dict]:
        """Returns list of ids present in database.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            List of dictionaries containing protein IDs and versions.
        """
        data = self.protein_repository.get_all_protein_ids(limit, offset)

        if data:
            files = [{"id": row[0], "version": row[1]} for row in data]
            return files

        return []

    def get_protein_ids_after_date(self, date: datetime) -> list[str]:
        """Retrieves ids of entries with files created after given date.

        Args:
            date: The cutoff date for filtering proteins.

        Returns:
            List of protein IDs created after the specified date.
        """
        ids = self.protein_repository.get_proteins_after_date(date)

        return ids

    def get_changes_after_date(
        self, start_date: datetime, change: Operations
    ) -> list[dict]:
        """Retrieves ids changed after given date.

        Args:
            start_date: The cutoff date for filtering changes.
            change: The type of change to filter by.

        Returns:
            List of dictionaries containing changed protein IDs and versions.
        """
        result = self.change_repository.get_changes_after_date(start_date, change)

        if result:
            ids = [{"id": row[0], "version": row[1]} for row in result]
            return ids
        return []

    def bulk_insert_new_proteins(self, ids: list[tuple]):
        """Inserts new file entries in bulk.

        Args:
            ids: List of protein IDs to insert.
        """
        values = []

        for id in ids:
            values.append({"id": id, "deprecated": False})

        self.protein_repository.insert_in_bulk(values)
