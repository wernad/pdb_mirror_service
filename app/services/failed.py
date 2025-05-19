"""Service module for managing failed fetch operations.

This module provides a service layer for handling failed fetch operations,
including tracking failed fetches and managing retry attempts.
"""

from sqlmodel import Session
from app.database.repositories import (
    FileRepository,
    FailedFetchRepository,
    ProteinRepository,
)

from app.database.models import FailedFetch
from app.log import log as log


class FailedFetchService:
    """Service class for managing failed fetch operations.

    This class provides methods for tracking and managing failed fetch operations,
    including inserting failed fetch records and retrieving failed fetch history.
    """

    file_repository: FileRepository
    failed_repository: FailedFetchRepository
    protein_repository: ProteinRepository

    def __init__(self, db: Session):
        """Initialize the failed fetch service with database session.

        Args:
            db: SQLModel database session.
        """
        self.failed_fetch_repository = FailedFetchRepository(db)
        self.file_repository = FileRepository(db)
        self.protein_repository = ProteinRepository(db)

    def insert_failed_fetch(self, protein_id: str, error: str) -> bool:
        """Inserts a record of a failed fetch operation.

        If the protein doesn't exist, creates a new protein entry first.

        Args:
            protein_id: The ID of the protein that failed to fetch.
            error: The error message describing why the fetch failed.

        Returns:
            True if insertion was successful, False otherwise.
        """
        protein = self.protein_repository.get_protein_by_id(protein_id=protein_id)

        if not protein:
            log.debug(f"Protein {protein_id} not found, inserting new protein entry.")
            self.protein_repository.insert_protein(protein_id=protein_id)

        version = (
            self.file_repository.get_latest_version_by_protein_id(protein_id=protein_id)
            + 1
        )
        result = self.failed_fetch_repository.insert_new_failed_fetch(
            protein_id=protein_id, version=version, error=error
        )

        return result

    def get_all_failed_fetches(self) -> list[FailedFetch]:
        """Retrieves all failed fetch records.

        Returns:
            List of all failed fetch records in the database.
        """
        return self.failed_fetch_repository.get_all_failed_fetches()
