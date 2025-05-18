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


class Padding(SQLModel):
    limit: int = Field(100, gt=0, le=1000000)
    offset: int = Field(0, ge=0)
