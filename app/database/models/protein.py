"""Database models for protein records.

This module defines SQLModel classes for protein records, including
base models, relationships, and pagination parameters.
"""

from typing import TYPE_CHECKING, List

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.database.models import File, FailedFetch, Change


class ProteinBase(SQLModel):
    """Base model for protein records.

    This model defines the basic structure for protein records,
    including the primary key and deprecated status.

    Args:
        id: The unique identifier for the protein.
        deprecated: Whether the protein is deprecated.
    """

    id: str = Field(primary_key=True)
    deprecated: bool = Field(nullable=False, default=False)


class Protein(ProteinBase, table=True):
    """Database model for protein records.

    This model represents the protein table in the database, including
    relationships to files, failed fetches, and changes.

    Args:
        files: List of files associated with this protein.
        failed: List of failed fetch attempts for this protein.
        changes: List of changes associated with this protein.
    """

    files: List["File"] = Relationship(back_populates="protein")
    failed: List["FailedFetch"] = Relationship(back_populates="protein")
    changes: List["Change"] = Relationship(back_populates="protein")


class Padding(SQLModel):
    """Model for pagination parameters.

    This model defines the structure for pagination parameters,
    including limit and offset values.

    Args:
        limit: Maximum number of records to return.
        offset: Number of records to skip.
    """

    limit: int = Field(100, gt=0, le=1000000)
    offset: int = Field(0, ge=0)
