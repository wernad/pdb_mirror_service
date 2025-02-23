from sqlmodel import Session
from app.database.repositories import ProteinRepository

from app.log import logger as log


class ProteinService:
    protein_repository: ProteinRepository

    def __init__(self, db: Session):
        self.protein_repository = ProteinRepository(db)

    def deprecate_protein(self, protein_id: str):
        """Deprecated given protein entry."""

        result = self.protein_repository.update_depricated(protein_id=protein_id, status=True)

        if not result:
            log.debug(f"Protein {protein_id} not found, inserting new protein entry.")
            self.protein_repository.insert_protein(protein_id=protein_id, deprecated=True)

    def bulk_insert_new_proteins(self, ids: list[tuple]):
        """Inserts new file entries in bulk."""
        values = []

        for id in ids:
            values.append({"protein_id": id, "deprecated": False})

        self.protein_repository.insert_in_bulk(values)
