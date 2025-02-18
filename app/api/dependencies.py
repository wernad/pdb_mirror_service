from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from app.database.database import engine
from app.services import FileService, FailedFetchService
from app.api.exceptions import UnsupportedIDFormat
from app.services.protein import ProteinService

__all__ = ["FileServiceDep", "FailedFetchServiceDep", "IDCheckDep"]


# Session


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# Protein


def get_protein_service(db: SessionDep) -> Generator[ProteinService, None, None]:
    yield ProteinService(db)


ProteinServiceDep = Annotated[ProteinService, Depends(get_protein_service)]


# File


def get_file_service(db: SessionDep) -> Generator[FileService, None, None]:
    yield FileService(db)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]


# Failed fetch


def get_failed_fetch_service(db: SessionDep) -> Generator[FailedFetchService, None, None]:
    yield FailedFetchService(db)


FailedFetchServiceDep = Annotated[FailedFetchService, Depends(get_failed_fetch_service)]


# ID handling


def check_protein_id(protein_id: str):
    if len(protein_id) == 4:
        protein_id = f"pdb_0000{protein_id}"
    elif len(protein_id) == 12 and protein_id.startswith("pdb_"):
        pass
    else:
        raise UnsupportedIDFormat(protein_id=protein_id)

    return protein_id


IDCheckDep = Annotated[str, Depends(check_protein_id)]
