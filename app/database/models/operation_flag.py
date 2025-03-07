from sqlmodel import Field, SQLModel


# 1 - added
# 2 - modified
# 3 - obsolete
class OperationFlagBase(SQLModel):
    name: str


class OperationFlag(OperationFlagBase, table=True):
    id: int = Field(primary_key=True)
