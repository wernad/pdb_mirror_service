"""Database models for operation flags.

This module defines SQLModel classes and enums for operation flags,
which are used to track different types of operations performed on proteins.
"""

from enum import Enum
from sqlmodel import Field, SQLModel


class Operations(Enum):
    """Enumeration of possible protein operations.

    This enum defines the different types of operations that can be
    performed on proteins in the system.

    Attributes:
        ADDED: Operation indicating a new protein was added.
        MODIFIED: Operation indicating a protein was modified.
        OBSOLETE: Operation indicating a protein is now obsolete.
    """

    ADDED = 1
    MODIFIED = 2
    OBSOLETE = 3


OPERATIONS_NAMES = {
    Operations.ADDED: "added",
    Operations.MODIFIED: "modified",
    Operations.OBSOLETE: "obsolete",
}


class OperationFlagBase(SQLModel):
    """Base model for operation flag records.

    This model defines the basic structure for operation flag records,
    including the operation name.

    Args:
        name: The name of the operation flag.
    """

    name: str


class OperationFlag(OperationFlagBase, table=True):
    """Database model for operation flag records.

    This model represents the operationflag table in the database,
    which stores predefined operation flags.

    Args:
        id: The unique identifier for the operation flag.
    """

    id: int = Field(primary_key=True)
