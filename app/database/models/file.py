from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, LargeBinary

if TYPE_CHECKING:
    from app.database.models import Protein


class FileBase(SQLModel):
    timestamp: datetime
    version: int = Field(nullable=False)
    file: LargeBinary = Field(nullable=False)
    deprecated: bool = Field(nullable=False)


class File(FileBase, table=True):
    id: int = Field(primary_key=True)
    protein_id: str = Field(foreign_key="proteid.name")

    protein: "Protein" = Relationship(back_populates="protein.files")
