from sqlmodel import select

from app.log import logger as log
from app.database.repositories.base import RepositoryBase
from app.database.models.protein import Protein


class ProteinRepository(RepositoryBase):
    """Repository for DB operations related to files."""

    def get_protein_by_id(self, protein_id: str) -> Protein:
        statement = select(Protein).where(Protein.id == protein_id)
        protein = self.db.exec(statement).first()

        return protein

    def insert_protein(self, protein_id: str) -> str:
        new_protein = Protein(id=protein_id)
        try:
            self.db.add(new_protein)
            self.db.commit()
            self.db.refresh(new_protein)
            log.debug(f"Inserted new protein entry {protein_id}")
        except Exception as e:
            self.db.rollback()
            log.error(f"Failed to insert new protein entry. Error: {str(e)}")

    def update_depricated(self, protein_id: str, status: bool):
        protein = self.get_protein_by_id(protein_id)

        if protein:
            try:
                protein.deprecated = status
                self.db.commit()
                self.db.refresh(protein)
                log.debug(f"Inserted new protein entry {protein_id}")
            except Exception as e:
                self.db.rollback()
                log.error(f"Failed to update status of protein {protein_id}. Error: {str(e)}")
        else:
            log.error(f"Protein with id {protein_id} not found.")
