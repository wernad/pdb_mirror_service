"""FastAPI dependency injection module.

This module provides dependency injection functions and types for FastAPI endpoints,
including database session management, service instantiation, and input validation.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from app.database.database import get_session
from app.services import FileService, FailedFetchService
from app.api.exceptions import UnsupportedIDFormat
from app.services.protein import ProteinService

__all__ = ["FileServiceDep", "FailedFetchServiceDep", "IDCheckDep"]


# Session


SessionDep = Annotated[Session, Depends(get_session)]


# Protein


def get_protein_service(db: SessionDep) -> Generator[ProteinService, None, None]:
    """Creates a ProteinService instance with the provided database session.

    Args:
        db: Database session dependency.

    Returns:
        A generator that yields a ProteinService instance.
    """
    yield ProteinService(db)


ProteinServiceDep = Annotated[ProteinService, Depends(get_protein_service)]


# File


def get_file_service(db: SessionDep) -> Generator[FileService, None, None]:
    """Creates a FileService instance with the provided database session.

    Args:
        db: Database session dependency.

    Returns:
        A generator that yields a FileService instance.
    """
    yield FileService(db)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]


# Failed fetch


def get_failed_fetch_service(
    db: SessionDep,
) -> Generator[FailedFetchService, None, None]:
    """Creates a FailedFetchService instance with the provided database session.

    Args:
        db: Database session dependency.

    Returns:
        A generator that yields a FailedFetchService instance.
    """
    yield FailedFetchService(db)


FailedFetchServiceDep = Annotated[FailedFetchService, Depends(get_failed_fetch_service)]


# ID handling


def check_protein_id(protein_id: str):
    """Validates and normalizes protein IDs.

    This function ensures protein IDs are in the correct format (either 4 characters
    or 12 characters starting with 'pdb_'). For 4-character IDs, it prepends 'pdb_0000'.

    Args:
        protein_id: The protein ID to validate and normalize.

    Returns:
        str: The normalized protein ID.

    Raises:
        UnsupportedIDFormat: If the protein ID is not in a supported format.
    """
    if len(protein_id) == 4:
        protein_id = f"pdb_0000{protein_id}"
    elif len(protein_id) == 12 and protein_id.startswith("pdb_"):
        pass
    else:
        raise UnsupportedIDFormat(protein_id=protein_id)

    return protein_id


IDCheckDep = Annotated[str, Depends(check_protein_id)]
