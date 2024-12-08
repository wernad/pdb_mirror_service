from sqlmodel import Session
from app.database.repositories import FileRepository, FailedFetchRepository, ProteinRepository

from app.database.models import FailedFetch
from app.log import logger as log


class FailedFetchService:
    file_repository: FileRepository
    failed_repository: FailedFetchRepository
    protein_repository: ProteinRepository

    def __init__(self, db: Session):
        self.failed_fetch_repository = FailedFetchRepository(db)
        self.file_repository = FileRepository(db)
        self.protein_repository = ProteinRepository(db)

    def insert_failed_fetch(self, protein_id: str, error: str) -> bool:
        protein = self.protein_repository.get_protein_by_id(protein_id=protein_id)

        if not protein:
            log.debug(f"Protein {protein_id} not found, inserting new protein entry.")
            self.protein_repository.insert_protein(protein_id=protein_id)

        version = self.file_repository.get_latest_version_by_protein_id(protein_id=protein_id) + 1
        result = self.failed_fetch_repository.insert_new_failed_fetch(
            protein_id=protein_id, version=version, error=error
        )

        return result

    def get_all_failed_fetches(self) -> list[FailedFetch]:
        return self.failed_fetch_repository.get_all_failed_fetches()
