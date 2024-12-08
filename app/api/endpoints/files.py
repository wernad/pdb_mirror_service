from datetime import datetime as dt
from requests import get
from ftplib import FTP

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.log import logger as log
from app.api.dependencies import FileServiceDep, FailedFetchServiceDep
from app.api.exceptions import FileNotFound, FileVersionNotFound
from app.config import PDB_FTP_URL, PDB_VIEW_URL

router = APIRouter()


def check_last_modified(ftp: FTP, path: str):
    log.debug(f"Checking files in path: {path}")

    ftp.cwd(path)
    items = ftp.mlsd("", ["modify"])
    dirs_to_check = []
    for name, metadata in items:
        if name in (".", ".."):
            continue

        file_date = dt.strptime(metadata["modify"], "%Y%m%d%H%M%S")
        date_dif = dt.now() - file_date

        if date_dif.days < 10:
            dirs_to_check.append(name)
    return dirs_to_check


@router.get("/")
async def get_files(file_service: FileServiceDep, failed_fetch_service: FailedFetchServiceDep):
    entries_path = "/pdb_versioned/data/entries"
    ftp = FTP(PDB_FTP_URL)
    if "230" in ftp.login():
        log.debug("Logged to FTP.")
        parent_dirs = check_last_modified(ftp, entries_path)
        print(parent_dirs)
        files_to_fetch = []
        n = 1
        for parent_dir in parent_dirs:
            path = f"{entries_path}/{parent_dir}"
            file_dirs = check_last_modified(ftp, path)
            print(file_dirs)
            files_to_fetch.extend([(parent_dir, file_name) for file_name in file_dirs])
            if n > 3:
                break

            n += 1
        print(files_to_fetch)

        for parent_dir, file_dir in files_to_fetch:
            file_name = f"{file_dir}_xyz.cif.gz"
            fetch_url = f"{PDB_VIEW_URL}{parent_dir}/{file_dir}/{file_name}"
            response = get(fetch_url)

            if not response.status_code == 200:
                log.error("Files response failed.")
                try:
                    processed_error = response.json()
                except Exception as _:
                    processed_error = response.text()
                failed_fetch_service.insert_failed_fetch(protein_id=file_dir, error=processed_error)
                continue

            content = response.content
            result = file_service.insert_new_version(protein_id=file_dir, file=content)

            if not result:
                failed_fetch_service.insert_failed_fetch(
                    protein_id=file_dir, error=f"Failure during insertion of new version. {result}"
                )

    return None


@router.get(
    "/{protein_id}/latest",
    name="Latest CIF",
    description="Returns latest version of CIF file for given protein, if it exists.",
)
async def get_latest_cif(file_service: FileServiceDep, protein_id: str):
    file = file_service.get_latest_by_protein_id(protein_id=protein_id)

    if not file:
        raise FileNotFound(protein_id)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}.cif"'}

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/version/{version}",
    name="CIF at version",
    description="Returns specific version of CIF file for given protein, if version and protein exist.",
)
async def get_cif_at_version(file_service: FileServiceDep, protein_id: str, version: int):
    print("###")
    file = file_service.get_by_version_and_protein_id(protein_id=protein_id, version=version)

    if not file:
        raise FileVersionNotFound(protein_id=protein_id, version=version)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_v{version}.cif"'}

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/date/{date}",
    name="Latest CIF prior to date",
    description="Returns latest of CIF file for given protein before given date.",
)
async def get_latest_cif_prior(file_service: FileServiceDep, protein_id: str, date: dt):
    print("@@@")
    file = file_service.get_latest_by_id_before_date(protein_id=protein_id, date=date)

    if not file:
        raise FileNotFound(protein_id=protein_id)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_{date}.cif"'}

    return PlainTextResponse(file, headers=headers)
