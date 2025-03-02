from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.database.models import Protein


class Change(SQLModel, table=True):
    id: int = Field(primary_key=True)
    timestamp: datetime
    protein_id: str = Field(foreign_key="protein.id")
    change_flag: int = Field(foreign_key="change_flag.value")

    protein: "Protein" = Relationship(back_populates="changes")
