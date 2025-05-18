from datetime import datetime

from sqlmodel import insert, select, and_

from app.database.repositories.base import RepositoryBase
from app.database.models import Change, Operations, File


class ChangeRepository(RepositoryBase):
    """Repository for DB operations related to changes in databasse."""

    def insert_bulk(self, values: list):
        """Inserts all new changes regarding file changes to database."""

        self.db.exec(insert(Change).values(values))
        self.db.commit()

    def get_changes_after_date(
        self, start_date: datetime, change: Operations
    ) -> list[str]:
        """Returns protein ids of files changed after given date."""

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
