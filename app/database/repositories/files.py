from datetime import datetime
from sqlmodel import select

from app.database.repositories.base import RepositoryBase
from app.database.models import File


class FileRepository(RepositoryBase):
    """Repository for DB operations related to files."""

    def get_latest_by_protein_id(self, protein_id: str) -> File:
        statement = select(File).where(File.protein_id == protein_id)
        file = self.db.exec(statement).first()

        return file

    def get_by_protein_id_at_version(self, protein_id: str, version: int) -> File:
        statement = select(File).where(File.protein_id == protein_id, File.version == version)
        file = self.db.exec(statement).first()

        return file

    def get_latest_by_id_before_date(self, protein_id: str, date: datetime) -> File:
        statement = select(File).where(File.protein_id == protein_id, File.timestamp <= date)
        file = self.db.exec(statement).first()

        return file
