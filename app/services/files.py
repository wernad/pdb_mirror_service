from sqlmodel import Session
from app.database.repositories import FileRepository

from app.database.models import File


class FileService:
    repository: FileRepository

    def __init__(self, db: Session):
        self.repository = FileRepository(db)

    def get_file_by_protein_id(self, protein_id: str) -> str:
        """Fetches BYTEA entry from database using repository and returns it as string."""

        data: File = self.repository.get_file_by_protein_id(protein_id)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None
