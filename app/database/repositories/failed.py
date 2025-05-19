"""Repository module for managing failed fetch records in the database.

This module provides a repository class for handling database operations related to
failed fetch attempts, including tracking and retrieval of failed operations.
"""

from datetime import datetime
from sqlmodel import select

from app.log import log as log
from app.database.repositories.base import RepositoryBase
from app.database.models import FailedFetch


class FailedFetchRepository(RepositoryBase):
    """Repository for managing failed fetch records in the database.

    This class provides methods for tracking and retrieving information about
    failed fetch operations, helping with error tracking and retry management.
    """

    def get_all_failed_fetches(self) -> list[FailedFetch]:
        """Retrieves all failed fetch records from the database.

        Returns:
            List of all failed fetch records.
        """
        statement = select(FailedFetch)
        files = self.db.exec(statement).all()

        return files

    def insert_new_failed_fetch(self, protein_id: str, version: int, error: str):
        """Inserts a new failed fetch record.

        Args:
            protein_id: The ID of the protein that failed to fetch.
            version: The version number that failed to fetch.
            error: The error message describing the failure.

        Returns:
            True if insertion was successful, False otherwise.
        """
        try:
            new_file = FailedFetch(
                fetch_date=datetime.now(),
                fetch_version=version,
                protein_id=protein_id,
                error=error,
            )
            self.db.add(new_file)
            self.db.commit()
            log.debug(
                f"Inserted failed fetch for version {version} and for protein {protein_id}"
            )
            return True
        except Exception as e:
            self.db.rollback()
            log.error(f"Failed to insert new failed fetch data. Error {str(e)}")
            return False
