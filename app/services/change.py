from sqlmodel import Session
from app.database.repositories import ChangeRepository

from app.database.models import ChangeInsert


class ChangeService:
    change_repository: ChangeRepository

    def __init__(self, db: Session):
        self.change_repository = ChangeRepository(db)

    def insert_bulk_added(self, entries: list[ChangeInsert]):
        """Inserts information about protein entry changes."""

        values = []
        for entry in entries:
            values.append(
                {
                    "protein_id": entry.protein_id,
                    "operation_flag": entry.operation_flag,
                    "timestamp": entry.timestamp,
                }
            )

        self.change_repository.insert_bulk(entries)
