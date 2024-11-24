from sqlmodel import select

from app.database.repositories.base import RepositoryBase
from app.database.models import File


# TODO possibly add services to handle manipulation of fetched data.
# TODO potentially change engine and repo to true async
class FileRepository(RepositoryBase):
    """Repository for DB operations related to files."""

    def get_file_by_protein_id(self, protein_id: str) -> bytes:
        statement = select(File).where(File.protein_id == protein_id)
        channels = self.db.exec(statement).first()

        return channels
