from datetime import datetime
from sqlmodel import select

from app.log import logger as log
from app.database.repositories.base import RepositoryBase
from app.database.models import FailedFetch


class FailedFetchRepository(RepositoryBase):
    """Repository for DB operations related to failed fetches."""

    def get_all_failed_fetches(self) -> list[FailedFetch]:
        statement = select(FailedFetch)
        files = self.db.exec(statement).all()

        return files

    def insert_new_failed_fetch(self, protein_id: str, version: int, error: str):
        """Inserts new file version of given protein id."""

        try:
            new_file = FailedFetch(fetch_date=datetime.now(), fetch_version=version, protein_id=protein_id, error=error)
            self.db.add(new_file)
            self.db.commit()
            self.db.refresh(new_file)
            log.debug(f"Inserted failed fetch for version {version} and for protein {protein_id}")
            return True
        except Exception as e:
            self.db.rollback()
            log.error(f"Failed to insert new failed fetch data. Error {str(e)}")
            return False
