from datetime import datetime
from sqlmodel import Session

from app.database.repositories import FileRepository, ProteinRepository
from app.database.models import FileBase, File, FileInsert, ChangeInsert
from app.log import logger as log
from app.database.repositories.change import ChangeRepository


class FileService:
    file_repository: FileRepository
    protein_repository: ProteinRepository
    change_repository: ChangeRepository

    def __init__(self, db: Session):
        self.file_repository = FileRepository(db)
        self.protein_repository = ProteinRepository(db)
        self.change_repository = ChangeRepository(db)

    def get_latest_by_protein_id(self, protein_id: str) -> bytes:
        """Fetches latest entry of given protein."""

        data: FileBase = self.file_repository.get_latest_by_protein_id(protein_id)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_latest_version_by_protein_id(self, protein_id: str) -> int:
        """Fetches latest version number of given file."""
        data: File = self.file_repository.get_latest_version_by_protein_id(protein_id)

        if data:
            return data.version

        return None

    def get_by_version_and_protein_id(self, protein_id: str, version: int) -> bytes | None:
        """Fetches specific version of a protein entry."""

        data: File = self.file_repository.get_by_protein_id_at_version(protein_id, version)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_latest_by_id_before_date(self, protein_id: str, date: datetime) -> bytes | None:
        """Fetches latest protein entry prior to specified date."""

        data: File = self.file_repository.get_latest_by_id_before_date(protein_id, date)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_new_files_after_date(self, date: datetime) -> list[bytes] | None:
        """Fetches newest proteins in a list after given date."""

        data: list[File] = self.file_repository.get_new_files_after_date(date)

        if data:
            output = []
            for entry in data:
                binary_file = entry.file
                output.append(bytes(binary_file))
            return output

        return None

    def insert_new_version(self, protein_id: str, file: bytes, version: int) -> bool:
        """Inserts a new version of given protein. If protein doesn't have an entry, create it."""
        protein = self.protein_repository.get_protein_by_id(protein_id=protein_id)

        if not protein:
            log.debug(f"Protein {protein_id} not found, inserting new protein entry.")
            self.protein_repository.insert_protein(protein_id=protein_id)

        result = self.file_repository.insert_new_version(protein_id=protein_id, file=file, version=version)
        return result

    def bulk_insert_new_files(self, files: list[FileInsert], changes: list[ChangeInsert]) -> None:
        """Inserts new file entries in bulk."""
        file_values = []
        change_values = []

        for file in files:
            file_values.append({"protein_id": file.protein_id, "version": file.version, "file": file.file})

        file_ids = self.file_repository.insert_in_bulk(file_values)

        for file_id, change in zip(file_ids, changes):
            change_values.append(
                {
                    "protein_id": change.protein_id,
                    "change_flag": change.operation_flag,
                    "file_id": file_id,
                    "timestamp": change.timestamp,
                }
            )
