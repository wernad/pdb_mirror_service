from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein, File


class ChangeInsert(SQLModel):
    timestamp: datetime
    protein_id: str = Field(foreign_key="protein.id")
    operation_flag: int = Field(foreign_key="operationflag.id")


class Change(ChangeInsert, table=True):
    id: int = Field(primary_key=True)
    file_id: int = Field(foreign_key="file.id", nullable=True)

    protein: "Protein" = Relationship(back_populates="changes")
    file: "File" = Relationship(back_populates="changes")
