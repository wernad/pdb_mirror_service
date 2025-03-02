from typing import TYPE_CHECKING, List

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.database.models import File, FailedFetch, Change


class ProteinBase(SQLModel):
    id: str = Field(primary_key=True)
    deprecated: bool = Field(nullable=False, default=False)


class Protein(ProteinBase, table=True):
    files: List["File"] = Relationship(back_populates="protein")
    failed: List["FailedFetch"] = Relationship(back_populates="protein")
    changes: List["Change"] = Relationship(back_populates="protein")
