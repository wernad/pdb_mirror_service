from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from app.database.database import engine
from app.services import FileService

__all__ = ["FileServiceDep"]


# Session


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# File


def get_file_service(db: SessionDep) -> Generator[FileService, None, None]:
    yield FileService(db)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
