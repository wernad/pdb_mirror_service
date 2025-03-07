from datetime import datetime
from sqlmodel import insert, select

from app.log import logger as log
from app.database.repositories.base import RepositoryBase
from app.database.models import FileBase, File, Change


class FileRepository(RepositoryBase):
    """Repository for DB operations related to files."""

    def get_latest_by_protein_id(self, protein_id: str) -> FileBase:
        statement = select(File).where(File.protein_id == protein_id).order_by(File.version.desc()).limit(1)
        file = self.db.exec(statement).first()

        return file

    def get_by_protein_id_at_version(self, protein_id: str, version: int) -> FileBase:
        statement = select(File).where(File.protein_id == protein_id, File.version == version)
        file = self.db.exec(statement).first()

        return file

    def get_latest_by_id_before_date(self, protein_id: str, date: datetime) -> FileBase:
        statement = (
            select(File)
            .join(Change, Change.file_id == File.id)
            .where(Change.protein_id == protein_id, Change.timestamp <= date)
            .order_by(Change.timestamp)
            .limit(1)
        )
        file = self.db.exec(statement).first()

        return file

    # TODO fix version handling as now it doesnt return correct value.
    def get_latest_version_by_protein_id(self, protein_id: str) -> int:
        file = self.get_latest_by_protein_id(protein_id=protein_id)

        if file:
            return file.version

        return 0

    def get_new_files_after_date(self, date: datetime) -> list[FileBase]:
        statement = select(File).join(Change, Change.file_id == File.id).where(Change.timestamp > date)

        files = self.db.exec(statement).all()

        return files

    def insert_new_version(self, protein_id: str, version: int, file: bytes):
        """Inserts new file version of given protein id."""

        new_file = File(timestamp=datetime.now(), version=version, file=file, protein_id=protein_id)

        try:
            self.db.add(new_file)
            self.db.commit()
            log.debug(f"Inserted file version {version} for protein {protein_id}")
            return True
        except Exception as e:
            log.error(f"Failed to insert new file. Error {str(e)}")
            self.db.rollback()
            return False

    def insert_in_bulk(self, file_values: list):
        """Inserts new file rows in bulk."""

        result = self.db.exec(insert(File).returning(File.id).values(file_values))
        self.db.commit()

        ids = [row.id for row in result]

        return ids
