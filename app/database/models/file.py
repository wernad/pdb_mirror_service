"""Database models for protein file records.

This module defines SQLModel classes for protein file records, including
base models, insert models, and relationships with proteins and changes.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein, Change


class FileBase(SQLModel):
    """Base model for protein file records.

    This model defines the basic structure for protein file records,
    including version and file content.

    Args:
        version: The version number of the file.
        file: The binary content of the file.
    """

    version: int = Field(nullable=False)
    file: bytes = Field(nullable=False)


class FileInsert(FileBase):
    """Model for inserting new protein file records.

    This model extends FileBase to include the protein ID for insertion.

    Args:
        protein_id: The ID of the protein this file belongs to.
    """

    protein_id: str = Field(foreign_key="protein.id")


class File(FileInsert, table=True):
    """Database model for protein file records.

    This model represents the file table in the database, including
    relationships to proteins and changes.

    Args:
        id: The unique identifier for the file.
        protein: The protein this file belongs to.
        changes: List of changes associated with this file.
    """

    id: int = Field(primary_key=True)

    protein: "Protein" = Relationship(back_populates="files")
    changes: list["Change"] = Relationship(back_populates="file")
