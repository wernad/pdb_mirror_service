from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein, Change


class FileBase(SQLModel):
    version: int = Field(nullable=False)
    file: bytes = Field(nullable=False)


class FileInsert(FileBase):
    protein_id: str = Field(foreign_key="protein.id")


class File(FileInsert, table=True):
    id: int = Field(primary_key=True)

    protein: "Protein" = Relationship(back_populates="files")
    changes: list["Change"] = Relationship(back_populates="file")
