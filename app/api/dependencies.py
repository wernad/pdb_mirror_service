from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from app.database.database import engine
from app.services import FileService, FailedFetchService

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

# Failed fetch


def get_failed_fetch_service(db: SessionDep) -> Generator[FailedFetchService, None, None]:
    yield FailedFetchService(db)


FailedFetchServiceDep = Annotated[FailedFetchService, Depends(get_failed_fetch_service)]
