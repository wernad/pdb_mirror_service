from contextlib import contextmanager
from collections.abc import Generator
from sqlmodel import Session, create_engine, SQLModel
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
from pydantic_core import MultiHostUrl
from os import environ

__all__ = ["get_session", "db_context", "create_db_and_tables"]

DATABASE_URL = str(
    MultiHostUrl.build(
        scheme="postgresql",
        username=environ.get("DB_USER", DB_USER),
        password=environ.get("DB_PASSWORD", DB_PASSWORD),
        host=environ.get("DB_HOST", DB_HOST),
        port=environ.get("DB_PORT", DB_PORT),
        path=environ.get("DB_NAME", DB_NAME),
    )
)


engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


db_context = contextmanager(get_session)


def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)
