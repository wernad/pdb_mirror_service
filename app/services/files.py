from datetime import datetime
from sqlmodel import Session
from app.database.repositories import FileRepository

from app.database.models import File


class FileService:
    repository: FileRepository

    def __init__(self, db: Session):
        self.repository = FileRepository(db)

    def get_latest_by_protein_id(self, protein_id: str) -> bytes:
        """Fetches latest entry of given protein."""

        data: File = self.repository.get_latest_by_protein_id(protein_id)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_by_version_and_protein_id(self, protein_id: str, version: int) -> bytes | None:
        """Fetches specific version of a protein entry."""

        data: File = self.repository.get_by_protein_id_at_version(protein_id, version)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_latest_before_date(self, protein_id: str, before_date: datetime) -> bytes | None:
        """Fetches latest protein entry prior to specified date."""

        data: File = self.repository.get_latest_by_id_before_date(protein_id, before_date)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None
