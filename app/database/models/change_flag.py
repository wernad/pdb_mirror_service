from sqlmodel import Field, SQLModel


# 0 - added
# 1 - modified
# 2 - obsolete
class ChangeFlagBase(SQLModel):
    value: int


class ChangeFlag(ChangeFlagBase, table=True):
    id: int = Field(primary_key=True)
