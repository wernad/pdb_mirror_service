from sqlmodel import insert, select

from app.database.repositories.base import RepositoryBase
from app.database.models import OperationFlag, Operations, OPERATIONS_NAMES

from app.log import log as log


class OperationFlagRepository(RepositoryBase):
    """Repository for DB operations related to operation flags."""

    def init_table(self):
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
