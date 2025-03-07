from sqlmodel import insert

from app.database.repositories.base import RepositoryBase
from app.database.models import ChangeInsert


class ChangeRepository(RepositoryBase):
    """Repository for DB operations related to changes in databasse."""

    def insert_bulk(self, values: list):
        """Inserts all new changes regarding file changes to database."""

        self.db.exec(insert(ChangeInsert).values(values))
        self.db.commit()
