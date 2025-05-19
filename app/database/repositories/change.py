"""Repository module for managing change records in the database.

This module provides a repository class for handling database operations related to
tracking changes in protein files, including bulk inserts and change history queries.
"""

from datetime import datetime

from sqlmodel import insert, select, and_

from app.database.repositories.base import RepositoryBase
from app.database.models import Change, Operations, File


class ChangeRepository(RepositoryBase):
    """Repository for managing change records in the database.

    This class provides methods for inserting and querying change records,
    tracking modifications to protein files over time.
    """

    def insert_bulk(self, values: list):
        """Inserts multiple change records into the database.

        Args:
            values: List of change records to insert.
        """
        self.db.exec(insert(Change).values(values))
        self.db.commit()

    def get_changes_after_date(
        self, start_date: datetime, change: Operations
    ) -> list[str]:
        """Retrieves protein IDs of files changed after a given date.

        Args:
            start_date: The cutoff date for filtering changes.
            change: The type of change to filter for.

        Returns:
            List of protein IDs that match the criteria.
        """
        statement = (
            select(Change.protein_id, File.version)
            .join(File, File.id == Change.file_id)
            .where(
                and_(
                    Change.timestamp > start_date,
                    Change.operation_flag == change.value,
                )
            )
        )

        result = self.db.exec(statement).all()

        return result
