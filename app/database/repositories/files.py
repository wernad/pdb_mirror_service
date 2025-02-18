from datetime import datetime
from sqlmodel import select

from app.log import logger as log
from app.database.repositories.base import RepositoryBase
from app.database.models import File


class FileRepository(RepositoryBase):
    """Repository for DB operations related to files."""

    def get_latest_by_protein_id(self, protein_id: str) -> File:
        statement = select(File).where(File.protein_id == protein_id).order_by(File.version.desc()).limit(1)
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

    # TODO fix version handling as now it doesnt return correct value.
    def get_latest_version_by_protein_id(self, protein_id: str) -> int:
        file = self.get_latest_by_protein_id(protein_id=protein_id)

        if file:
            return file.version

        return 0

    def get_new_files_after_date(self, date: datetime) -> list[File]:
        statement = select(File).where(File.timestamp > date)

        files = self.db.exec(statement).all()

        return files

    def insert_new_version(self, protein_id: str, version: int, file: bytes):
        """Inserts new file version of given protein id."""

        new_file = File(timestamp=datetime.now(), version=version, file=file, protein_id=protein_id)

        try:
            self.db.add(new_file)
            self.db.commit()
            self.db.refresh(new_file)
            log.debug(f"Inserted file version {version} for protein {protein_id}")
            return True
        except Exception as e:
            log.error(f"Failed to insert new file. Error {str(e)}")
            self.db.rollback()
            return False
