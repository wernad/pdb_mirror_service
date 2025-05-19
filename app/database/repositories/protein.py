"""Repository module for managing protein records in the database.

This module provides a repository class for handling database operations related to
proteins, including retrieval, insertion, and status management.
"""

from datetime import datetime
from sqlmodel import insert, select, or_, func

from app.log import log as log
from app.database.repositories.base import RepositoryBase
from app.database.models import Protein, Change, Operations, File


class ProteinRepository(RepositoryBase):
    """Repository for managing protein records in the database.

    This class provides methods for retrieving, inserting, and managing
    protein records and their status.
    """

    def get_protein_by_id(self, protein_id: str) -> Protein:
        """Retrieves a protein record by its ID.

        Args:
            protein_id: The ID of the protein to fetch.

        Returns:
            The protein record if found.
        """
        statement = select(Protein).where(Protein.id == protein_id)
        protein = self.db.exec(statement).first()

        return protein

    def get_total_count(self) -> int:
        """Retrieves the total count of protein records.

        Returns:
            The total number of protein records.
        """
        statement = select(func.count(Protein.id))

        result = self.db.exec(statement).first()

        return result

    def get_all_protein_ids(self, limit: int, offset: int) -> list[str]:
        """Retrieves protein IDs with their latest version numbers.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            List of protein IDs with their latest versions.
        """
        statement = (
            select(Protein.id, func.max(File.version).label("version"))
            .join(File, File.protein_id == Protein.id)
            .group_by(Protein.id)
            .order_by(Protein.id)
        )

        if limit:
            statement = statement.limit(limit)

        if offset:
            statement = statement.offset(offset)

        result = self.db.exec(statement).all()

        return result

    def get_proteins_after_date(self, date: datetime) -> list[str]:
        """Retrieves proteins with files created after a given date.

        Args:
            date: The cutoff date for filtering proteins.

        Returns:
            List of protein IDs that match the criteria.
        """
        statement = (
            select(Protein.id)
            .join(Change, Change.protein_id == Protein.id)
            .where(
                Change.timestamp > date,
                or_(
                    Change.operation_flag == Operations.ADDED.value,
                    Change.operation_flag == Operations.MODIFIED.value,
                ),
            )
        )

        result = self.db.exec(statement).all()

        return result

    def insert_protein(self, protein_id: str, deprecated: bool = False) -> str:
        """Inserts a new protein record.

        Args:
            protein_id: The ID of the protein to insert.
            deprecated: Whether the protein is deprecated.

        Returns:
            The ID of the inserted protein.
        """
        new_protein = Protein(id=protein_id, deprecated=deprecated)
        try:
            self.db.add(new_protein)
            self.db.commit()
            log.debug(f"Inserted new protein entry {protein_id}")
        except Exception as e:
            self.db.rollback()
            log.error(f"Failed to insert new protein entry. Error: {str(e)}")

    def update_depricated(self, protein_id: str, status: bool):
        """Updates the deprecated status of a protein.

        Args:
            protein_id: The ID of the protein to update.
            status: The new deprecated status.

        Returns:
            True if update was successful, False otherwise.
        """
        protein = self.get_protein_by_id(protein_id)

        if protein:
            try:
                protein.deprecated = status
                self.db.commit()
                self.db.refresh(protein)
                log.debug(f"Inserted new protein entry {protein_id}")
                return True
            except Exception as e:
                self.db.rollback()
                log.error(
                    f"Failed to update status of protein {protein_id}. Error: {str(e)}"
                )
        else:
            log.error(f"Protein with id {protein_id} not found.")
            return False

    def insert_in_bulk(self, values: list):
        """Inserts multiple protein records in a single operation.

        Args:
            values: List of protein records to insert.
        """
        self.db.exec(insert(Protein).values(values))
        self.db.commit()
