"""Database models for failed fetch records.

This module defines SQLModel classes for tracking failed fetch operations,
including error details, timestamps, and relationships with proteins.
"""

from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein


class FailedFetchBase(SQLModel):
    """Base model for failed fetch records.

    This model defines the basic structure for failed fetch records,
    including error details and fetch information.

    Args:
        error: The error message describing the failure.
        fetch_date: The date and time when the fetch was attempted.
        fetch_version: The version number that was being fetched.
    """

    error: str = Field(nullable=False)
    fetch_date: datetime = Field(nullable=False)
    fetch_version: int = Field(nullable=False)


class FailedFetch(FailedFetchBase, table=True):
    """Database model for failed fetch records.

    This model represents the failed_fetch table in the database,
    including relationships to proteins and operation flags.

    Args:
        id: The unique identifier for the failed fetch record.
        operation_flag: The ID of the operation flag associated with this failure.
        protein_id: The ID of the protein that failed to fetch.
        protein: The protein associated with this failed fetch.
    """

    id: int = Field(primary_key=True)
    operation_flag: int = Field(foreign_key="operationflag.id")
    protein_id: str = Field(foreign_key="protein.id")

    protein: "Protein" = Relationship(back_populates="failed")
