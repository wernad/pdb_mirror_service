from sqlmodel import create_engine, SQLModel
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
from pydantic_core import MultiHostUrl

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


def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)
