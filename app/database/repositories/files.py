"""Repository module for managing protein file records in the database.

This module provides a repository class for handling database operations related to
protein files, including version management, file retrieval, and bulk operations.
"""

from datetime import datetime
from sqlmodel import insert, select

from app.log import log as log
from app.database.repositories.base import RepositoryBase
from app.database.models import FileBase, File, Change


class FileRepository(RepositoryBase):
    """Repository for managing protein file records in the database.

    This class provides methods for retrieving, inserting, and managing
    protein file records and their versions.
    """

    def get_latest_by_protein_id(self, protein_id: str) -> FileBase:
        """Retrieves the latest version of a protein file.

        Args:
            protein_id: The ID of the protein to fetch.

        Returns:
            The latest file record for the protein.
        """
        statement = (
            select(File)
            .where(File.protein_id == protein_id)
            .order_by(File.version.desc())
            .limit(1)
        )
        file = self.db.exec(statement).first()

        return file

    def get_by_protein_id_at_version(self, protein_id: str, version: int) -> FileBase:
        """Retrieves a specific version of a protein file.

        Args:
            protein_id: The ID of the protein to fetch.
            version: The specific version to retrieve.

        Returns:
            The file record for the specified version.
        """
        statement = select(File).where(
            File.protein_id == protein_id, File.version == version
        )
        file = self.db.exec(statement).first()

        return file

    def get_latest_by_id_before_date(self, protein_id: str, date: datetime) -> FileBase:
        """Retrieves the latest version of a protein file before a given date.

        Args:
            protein_id: The ID of the protein to fetch.
            date: The cutoff date for the file version.

        Returns:
            The latest file record before the specified date.
        """
        statement = (
            select(File)
            .join(Change, Change.file_id == File.id)
            .where(Change.protein_id == protein_id, Change.timestamp <= date)
            .order_by(Change.timestamp)
            .limit(1)
        )
        file = self.db.exec(statement).first()

        return file

    # TODO fix version handling as now it doesnt return correct value.
    def get_latest_version_by_protein_id(self, protein_id: str) -> int:
        """Retrieves the latest version number for a protein.

        Args:
            protein_id: The ID of the protein to check.

        Returns:
            The latest version number, or 0 if no versions exist.
        """
        file = self.get_latest_by_protein_id(protein_id=protein_id)

        if file:
            return file.version

        return 0

    def get_new_files_after_date(self, date: datetime) -> list[FileBase]:
        """Retrieves all new files added after a given date.

        Args:
            date: The cutoff date for filtering files.

        Returns:
            List of file records added after the specified date.
        """
        statement = (
            select(File)
            .join(Change, Change.file_id == File.id)
            .where(Change.timestamp > date)
        )

        files = self.db.exec(statement).all()

        return files

    def insert_new_version(self, protein_id: str, version: int, file: bytes):
        """Inserts a new version of a protein file.

        Args:
            protein_id: The ID of the protein.
            version: The version number to insert.
            file: The file content to store.

        Returns:
            True if insertion was successful, False otherwise.
        """
        new_file = File(
            timestamp=datetime.now(), version=version, file=file, protein_id=protein_id
        )

        try:
            self.db.add(new_file)
            self.db.commit()
            log.debug(f"Inserted file version {version} for protein {protein_id}")
            return True
        except Exception as e:
            log.error(f"Failed to insert new file. Error {str(e)}")
            self.db.rollback()
            return False

    def insert_in_bulk(self, file_values: list):
        """Inserts multiple file records in a single operation.

        Args:
            file_values: List of file records to insert.

        Returns:
            List of IDs for the inserted records.
        """
        statement = insert(File).values(file_values).returning(File.id)
        result = self.db.exec(statement)
        self.db.commit()

        ids = [row[0] for row in result.all()]

        return ids
