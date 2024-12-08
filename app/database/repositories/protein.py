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
            return True
        except Exception as e:
            self.db.rollback()
            log.error(f"Failed to insert new protein entry. Error: {str(e)}")
            return False
