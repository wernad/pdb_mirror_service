"""Database configuration and management module.

This module provides database connection management, table creation,
and initialization functionality for the PDB Mirror application.
"""

from contextlib import contextmanager
from collections.abc import Generator
from os import environ, getpid
from time import sleep

from sqlmodel import Session, create_engine, SQLModel, text, inspect
from pydantic_core import MultiHostUrl

from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
from app.database.repositories import OperationFlagRepository


from app.log import log as log

__all__ = ["get_session", "db_context", "create_db_and_tables"]

DATABASE_URL = str(
    MultiHostUrl.build(
        scheme="postgresql",
        username=environ.get("POSTGRES_USER", DB_USER),
        password=environ.get("POSTGRES_PASSWORD", DB_PASSWORD),
        host=environ.get("POSTGRES_HOST", DB_HOST),
        port=int(port) if (port := environ.get("POSTGRES_PORT", None)) else DB_PORT,
        path=environ.get("POSTGRES_NAME", DB_NAME),
    )
)


engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    """Creates a new database session.

    Returns:
        A generator that yields a database session.
    """
    with Session(engine) as session:
        yield session
        session.expunge_all()


db_context = contextmanager(get_session)

REQUIRED_TABLES = [
    "change",
    "failedfetch",
    "file",
    "operationflag",
    "protein",
]


def check_if_tables_exist():
    """Checks if all required database tables exist.

    Returns:
        bool: True if all required tables exist, False otherwise.
    """
    inspector = inspect(engine)

    for table in REQUIRED_TABLES:
        if not inspector.has_table(table):
            return False

    return True


def create_db_and_tables():
    """Creates all database tables defined in SQLModel models."""
    log.debug("Creating database and tables.")
    SQLModel.metadata.create_all(bind=engine)
    log.debug("Database and tables created and filled successfully.")


def init_flag_data():
    """Initializes flag data in the database.

    This function inserts initial data into tables that store flag-like data
    (method, category, source). It uses a database lock to ensure only one
    process can perform the initialization at a time.

    The function will wait if another process is already initializing the data.
    """
    log.debug("Inserting flag data to tables.")
    with db_context() as db:
        log.debug(f"Fill DB -- WORKER {getpid()} -- Attempting to acquire lock...")
        try:
            lock_id = "12345"
            lock_acquired = db.exec(
                text(f"SELECT pg_try_advisory_lock({lock_id})")
            ).scalar()

            if lock_acquired:
                log.debug(
                    f"Fill DB -- WORKER {getpid()} -- Lock acquired, inserting data..."
                )
                operation_repo = OperationFlagRepository(db)

                if operation_repo.init_table():
                    log.debug("Flag data inserted successfully.")
            else:
                # Another worker is already inseting data, wait for completion.
                log.debug(
                    f"Fill DB -- WORKER {getpid()} -- Waiting for data to be inserted by another worker..."
                )
                while not check_if_tables_exist():
                    log.debug(f"Fill DB -- WORKER {getpid()} - Waiting...")
                    sleep(5)

                log.debug(f"Fill DB -- WORKER {getpid()} -- Done waiting")
        except Exception as e:
            log.debug(f"Fill DB -- Error during table data initialization: {e}")
