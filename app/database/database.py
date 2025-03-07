from contextlib import contextmanager
from collections.abc import Generator
from sqlmodel import Session, create_engine, SQLModel
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
from pydantic_core import MultiHostUrl

__all__ = ["get_session", "db_context", "create_db_and_tables"]

DATABASE_URL = str(
    MultiHostUrl.build(
        scheme="postgresql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        path=DB_NAME,
    )
)


engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


db_context = contextmanager(get_session)


def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)
