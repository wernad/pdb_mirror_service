from datetime import datetime
from sqlmodel import Session
from app.database.repositories import ProteinRepository

from app.log import logger as log


class ProteinService:
    protein_repository: ProteinRepository

    def __init__(self, db: Session):
        self.protein_repository = ProteinRepository(db)

    def deprecate_protein(self, protein_id: str):
        """Deprecated given protein entry."""

        result = self.protein_repository.update_depricated(
            protein_id=protein_id, status=True
        )

        if not result:
            log.debug(f"Protein {protein_id} not found, inserting new protein entry.")
            self.protein_repository.insert_protein(
                protein_id=protein_id, deprecated=True
            )
            return True
        return False

    def get_protein_ids_after_date(self, date: datetime) -> list[str]:
        """Retrieves ids of entries with files created after given date."""
        ids = self.protein_repository.get_proteins_after_date(date)

        return ids

    def bulk_insert_new_proteins(self, ids: list[tuple]):
        """Inserts new file entries in bulk."""
        values = []

        for id in ids:
            values.append({"id": id, "deprecated": False})

        self.protein_repository.insert_in_bulk(values)
