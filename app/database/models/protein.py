from typing import TYPE_CHECKING, List

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.database.models import File


class ProteinBase(SQLModel):
    proteid_id: str = Field(primary_key=True)


class Protein(ProteinBase, table=True):
    files: List["File"] = Relationship(back_populates="protein")
