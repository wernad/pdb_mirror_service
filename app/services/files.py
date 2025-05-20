"""Service module for managing protein file operations.

This module provides a service layer for handling protein file-related operations,
including file retrieval, version management, and bulk file operations.
"""

from datetime import datetime
from sqlmodel import Session

from app.database.repositories import FileRepository, ProteinRepository
from app.database.models import FileBase, File, FileInsert, ChangeInsert
from app.log import log as log
from app.database.repositories.change import ChangeRepository


class FileService:
    """Service class for managing protein file operations.

    This class provides methods for interacting with protein files in the database,
    including file retrieval, version management, and bulk file operations.
    """

    file_repository: FileRepository
    protein_repository: ProteinRepository
    change_repository: ChangeRepository

    def __init__(self, db: Session):
        """Initialize the file service with database session.

        Args:
            db: SQLModel database session.
        """
        self.file_repository = FileRepository(db)
        self.protein_repository = ProteinRepository(db)
        self.change_repository = ChangeRepository(db)

    def get_latest_by_protein_id(self, protein_id: str) -> bytes:
        """Fetches latest entry of given protein.

        Args:
            protein_id: The ID of the protein to fetch.

        Returns:
            The latest file content if found, None otherwise.
        """
        data: FileBase = self.file_repository.get_latest_by_protein_id(protein_id)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_latest_version_by_protein_id(self, protein_id: str) -> int:
        """Fetches latest version number of given file.

        Args:
            protein_id: The ID of the protein to fetch version for.

        Returns:
            The latest version number if found, None otherwise.
        """
        data: File = self.file_repository.get_latest_version_by_protein_id(protein_id)

        if data is not None:
            return data.version

        return None

    def get_by_version_and_protein_id(
        self, protein_id: str, version: int
    ) -> bytes | None:
        """Fetches specific version of a protein entry.

        Args:
            protein_id: The ID of the protein to fetch.
            version: The specific version to fetch.

        Returns:
            The file content if found, None otherwise.
        """
        data: File = self.file_repository.get_by_protein_id_at_version(
            protein_id, version
        )

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_latest_by_id_before_date(
        self, protein_id: str, date: datetime
    ) -> bytes | None:
        """Fetches latest protein entry prior to specified date.

        Args:
            protein_id: The ID of the protein to fetch.
            date: The cutoff date for the file version.

        Returns:
            The file content if found, None otherwise.
        """
        data: File = self.file_repository.get_latest_by_id_before_date(protein_id, date)

        if data:
            binary_file = data.file
            return bytes(binary_file)

        return None

    def get_new_files_after_date(self, date: datetime) -> list[bytes] | None:
        """Fetches newest proteins in a list after given date.

        Args:
            date: The cutoff date for filtering files.

        Returns:
            List of file contents if found, None otherwise.
        """
        data: list[File] = self.file_repository.get_new_files_after_date(date)

        if data:
            output = []
            for entry in data:
                binary_file = entry.file
                output.append(bytes(binary_file))
            return output

        return None

    def insert_new_version(self, protein_id: str, file: bytes, version: int) -> bool:
        """Inserts a new version of given protein.

        If protein doesn't have an entry, creates it first.

        Args:
            protein_id: The ID of the protein to insert.
            file: The file content to insert.
            version: The version number of the file.

        Returns:
            True if insertion was successful, False otherwise.
        """
        protein = self.protein_repository.get_protein_by_id(protein_id=protein_id)

        if not protein:
            log.debug(f"Protein {protein_id} not found, inserting new protein entry.")
            self.protein_repository.insert_protein(protein_id=protein_id)

        result = self.file_repository.insert_new_version(
            protein_id=protein_id, file=file, version=version
        )
        return result

    def bulk_insert_new_files(
        self, files: list[FileInsert], changes: list[ChangeInsert]
    ) -> None:
        """Inserts new file entries in bulk.

        Args:
            files: List of file objects to insert.
            changes: List of change objects to insert.
        """
        file_values = []
        change_values = []

        for file in files:
            file_values.append(
                {
                    "protein_id": file.protein_id,
                    "version": file.version,
                    "file": file.file,
                }
            )

        file_ids = self.file_repository.insert_in_bulk(file_values)

        for file_id, change in zip(file_ids, changes):
            change_values.append(
                {
                    "protein_id": change.protein_id,
                    "operation_flag": change.operation_flag,
                    "file_id": file_id,
                    "timestamp": change.timestamp,
                }
            )

        self.change_repository.insert_bulk(change_values)
