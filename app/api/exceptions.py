from datetime import datetime
from fastapi import HTTPException


class FileNotFound(HTTPException):
    def __init__(self, protein_id: str):
        self.status_code = 404
        self.detail = f"File entry for protein '{protein_id}' not found."


class FileVersionNotFound(HTTPException):
    def __init__(self, protein_id: str, version: int):
        self.status_code = 404
        self.detail = f"File entry for protein '{protein_id}' at version {version} not found."


class UnsupportedIDFormat(HTTPException):
    def __init__(self, protein_id: str):
        self.status_code = 400
        self.detail = f"Given protein id is in unsupported format ({protein_id}). Use 4 or 12 character format. More info on: https://proteopedia.org/wiki/index.php/Pdb_code"


class NoFilesAfterDate(HTTPException):
    def __init__(self, date: datetime):
        self.status_code = 404
        self.detail = f"No new files after given date {str(date)}."


class UnexpectedSearchError(HTTPException):
    def __init__(self, code: int, error: str):
        self.status_code = code
        self.detail = f"Search API returned unexpected error: {error}"


class UnexpectedDataError(HTTPException):
    def __init__(self, code: int, error: str):
        self.status_code = code
        self.detail = f"Data API returned unexpected error: {error}"
