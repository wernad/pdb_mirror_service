from fastapi import HTTPException


class FileNotFound(HTTPException):
    def __init__(self, protein_id: str):
        self.status_code = 404
        self.detail = f"File entry for protein '{protein_id}' not found."


class FileVersionNotFound(HTTPException):
    def __init__(self, protein_id: str, version: int):
        self.status_code = 404
        self.detail = f"File entry for protein '{protein_id}' at version {version} not found."
