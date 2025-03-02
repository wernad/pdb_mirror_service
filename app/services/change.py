from sqlmodel import Session
from app.database.repositories import ChangeRepository

from app.database.models import Change
from app.log import logger as log


# TODO
class ChangeService:
    change_repository: ChangeRepository

    def __init__(self, db: Session):
        self.change_repository = ChangeRepository(db)
