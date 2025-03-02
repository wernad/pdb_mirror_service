from datetime import datetime
from sqlmodel import insert, select

from app.log import logger as log
from app.database.repositories.base import RepositoryBase
from app.database.models import File


# TODO
class ChangeRepository(RepositoryBase):
    """Repository for DB operations related to changes in databasse."""
