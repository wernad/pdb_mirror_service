"""Database models for tracking changes to protein files.

This module defines SQLModel classes for tracking changes to protein files,
including the relationships between changes, proteins, and files.
"""

from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein, File


class ChangeInsert(SQLModel):
    """Model for inserting new change records.

    This model defines the structure for creating new change records,
    including timestamps, protein IDs, operation flags, and file IDs.

    Args:
        timestamp: When the change occurred.
        protein_id: The ID of the protein that changed.
        operation_flag: The type of change operation.
        file_id: The ID of the file associated with the change.
    """

    timestamp: datetime
    protein_id: str = Field(foreign_key="protein.id")
    operation_flag: int = Field(foreign_key="operationflag.id")
    file_id: int = Field(foreign_key="file.id", nullable=True)


class Change(ChangeInsert, table=True):
    """Database model for change records.

    This model represents the change table in the database, including
    relationships to proteins and files.

    Args:
        id: The primary key for the change record.
        protein: The protein associated with this change.
        file: The file associated with this change.
    """

    id: int = Field(primary_key=True)

    protein: "Protein" = Relationship(back_populates="changes")
    file: "File" = Relationship(back_populates="changes")
