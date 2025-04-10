from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein


class FailedFetchBase(SQLModel):
    error: str = Field(nullable=False)
    fetch_date: datetime = Field(nullable=False)
    fetch_version: int = Field(nullable=False)


class FailedFetch(FailedFetchBase, table=True):
    id: int = Field(primary_key=True)
    operation_flag: int = Field(foreign_key="operationflag.id")
    protein_id: str = Field(foreign_key="protein.id")

    protein: "Protein" = Relationship(back_populates="failed")
