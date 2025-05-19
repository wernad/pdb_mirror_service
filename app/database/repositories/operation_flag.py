"""Repository module for managing operation flag records in the database.

This module provides a repository class for handling database operations related to
operation flags, including initialization and management of predefined flags.
"""

from sqlmodel import insert, select

from app.database.repositories.base import RepositoryBase
from app.database.models import OperationFlag, Operations, OPERATIONS_NAMES

from app.log import log as log


class OperationFlagRepository(RepositoryBase):
    """Repository for managing operation flag records in the database.

    This class provides methods for initializing and managing operation flags,
    which are used to track different types of operations on protein files.
    """

    def init_table(self):
        """Initializes the operation flag table with predefined values.

        This method checks if the table is empty and, if so, inserts the
        predefined operation flags. If the table already has data, it skips
        initialization.

        Returns:
            True if initialization was performed, False if skipped.
        """
        statement = select(OperationFlag.id, OperationFlag.name)

        result = self.db.exec(statement).all()

        if result:
            log.debug(
                f"Operation flag table is not empty, skipping initialization. Present flags: {result}"
            )

            return False

        values = [
            {"id": operation.value, "name": OPERATIONS_NAMES[operation]}
            for operation in Operations
        ]

        statement = insert(OperationFlag).values(values)

        result = self.db.exec(statement)
        self.db.commit()

        log.debug(f"Inserted predefined operation flags: {values}")

        return True
