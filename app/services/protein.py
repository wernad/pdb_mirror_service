from datetime import datetime

from sqlmodel import Session
from app.database.repositories import ProteinRepository, ChangeRepository

from app.log import log as log
from app.database.models.operation_flag import Operations


class ProteinService:
    protein_repository: ProteinRepository
    change_repository: ChangeRepository

    def __init__(self, db: Session):
        self.protein_repository = ProteinRepository(db)
        self.change_repository = ChangeRepository(db)

    def get_total_count(self) -> int:
        """Returns total number of protein entries."""
        count = self.protein_repository.get_total_count()

        return count

    def get_all_ids(self, limit: int, offset: int) -> list[dict]:
        """Returns list of ids present in database."""

        data = self.protein_repository.get_all_protein_ids(limit, offset)

        if data:
            files = [{"id": row[0], "version": row[1]} for row in data]
            return files

        return []

    def get_protein_ids_after_date(self, date: datetime) -> list[str]:
        """Retrieves ids of entries with files created after given date."""
        ids = self.protein_repository.get_proteins_after_date(date)

        return ids

    def get_changes_after_date(
        self, start_date: datetime, change: Operations
    ) -> list[dict]:
        """Retrieves ids changed after given date"""

        result = self.change_repository.get_changes_after_date(start_date, change)

        if result:
            ids = [{"id": row[0], "version": row[1]} for row in result]
            return ids
        return []

    def bulk_insert_new_proteins(self, ids: list[tuple]):
        """Inserts new file entries in bulk."""
        values = []

        for id in ids:
            values.append({"id": id, "deprecated": False})

        self.protein_repository.insert_in_bulk(values)
