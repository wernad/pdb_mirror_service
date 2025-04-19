from enum import Enum
from sqlmodel import Field, SQLModel


class Operations(Enum):
    ADDED = 1
    MODIFIED = 2
    OBSOLETE = 3


OPERATIONS_NAMES = {
    Operations.ADDED: "added",
    Operations.MODIFIED: "modified",
    Operations.OBSOLETE: "obsolete",
}


class OperationFlagBase(SQLModel):
    name: str


class OperationFlag(OperationFlagBase, table=True):
    id: int = Field(primary_key=True)
