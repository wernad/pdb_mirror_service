from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein


class FileBase(SQLModel):
    timestamp: datetime
    version: int = Field(nullable=False)
    file: bytes = Field(nullable=False)
    deprecated: bool = Field(nullable=False)


class File(FileBase, table=True):
    id: int = Field(primary_key=True)
    protein_id: str = Field(foreign_key="protein.id")

    protein: "Protein" = Relationship(back_populates="files")
