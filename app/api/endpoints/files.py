from datetime import datetime as dt
from requests import get
from ftplib import FTP
from subprocess import Popen

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.log import logger as log
from app.api.dependencies import FileServiceDep, FailedFetchServiceDep, IDCheckDep
from app.api.exceptions import FileNotFound, FileVersionNotFound, NoFilesAfterDate
from app.config import PDB_HTTP_FILE_AGE, PDB_RSYNC_COMMAND, PDB_RSYNC_URL, PDB_HTTP_VIEW_URL

router = APIRouter()


def create_subprocess(path: str):
    """Wrapper for subprocess creation."""
    log.debug(f"Creating a subprocess for path: {path}")
    cmd = PDB_RSYNC_URL + path
    process = Popen(cmd)
    log.debug("Subprocess created.")

    return process


def run_rsync():
    """Runs rsync command and returns the output for a given url, if any."""
    log.debug("Starting subprocesses for rsync commands.")
    entries_path = "/entries"
    removed_path = "/removed"

    p_entries = create_subprocess(entries_path)
    p_removed = create_subprocess(removed_path)

    log.debug("Waiting for subprocesses to finish.")

    output = []
    for p in [p_entries, p_removed]:
        stdout, stderr = p.communicate()
        if stderr:
            output.append(None)
            log.error(f"Command '{p.args}' failed: \n{stderr}")
        else:
            output.append(stdout)
    log.debug("RSync finished.")
    return output


def get_removed():
    """Finds all removed entries from last week via Search API."""
    ...


def get_entries():
    """Finds all new entries from last week via Search API."""
    ...


def get_ids_with_pagination(url: str, start: int = 0, limit: int = 100):
    """Fetches ids of data entries with paginated result."""
    ...


def get_files_from_ids(file_names: list[str]):
    """Fetches CIF files from file server."""
    ...


# TODO rewrite to use Search API.
# removed rcsb_accession_info.deposit_date
# modified rcsb_accession_info.revision_date
@router.get("/")
async def get_files(file_service: FileServiceDep, failed_fetch_service: FailedFetchServiceDep):
    #     for parent_dir, file_dir in files_to_fetch:
    #         file_name = f"{file_dir}_xyz.cif.gz"
    #         fetch_url = f"{PDB_HTTP_VIEW_URL}{parent_dir}/{file_dir}/{file_name}"
    #         response = get(fetch_url)

    #         if not response.status_code == 200:
    #             log.error("Files response failed.")
    #             try:
    #                 processed_error = response.json()
    #             except Exception as _:
    #                 processed_error = response.text()
    #             failed_fetch_service.insert_failed_fetch(protein_id=file_dir, error=processed_error)
    #             continue

    #         content = response.content
    #         result = file_service.insert_new_version(protein_id=file_dir, file=content)

    #         if not result:
    #             failed_fetch_service.insert_failed_fetch(
    #                 protein_id=file_dir, error=f"Failure during insertion of new version. {result}"
    #             )

    return None


@router.get(
    "/{protein_id}/latest",
    name="Latest CIF",
    description="Returns latest version of CIF file for given protein, if it exists.",
)
async def get_latest_cif(file_service: FileServiceDep, protein_id: IDCheckDep):
    log.info(f"Received request for latest cif file with id {protein_id}")
    file = file_service.get_latest_by_protein_id(protein_id=protein_id)

    if not file:
        log.error(f"File with id {protein_id} not found.")
        raise FileNotFound(protein_id)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}.cif"'}

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/version/{version}",
    name="CIF at version",
    description="Returns specific version of CIF file for given protein, if version and protein exist.",
)
async def get_cif_at_version(file_service: FileServiceDep, protein_id: IDCheckDep, version: int):
    log.info(f"Received request for cif file with id {protein_id} at version {version}")
    file = file_service.get_by_version_and_protein_id(protein_id=protein_id, version=version)

    if not file:
        log.error(f"File for id {protein_id} at version {version} not found.")
        raise FileVersionNotFound(protein_id=protein_id, version=version)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_v{version}.cif"'}

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/date/{date}",
    name="Latest CIF prior to date",
    description="Returns latest CIF file for given protein before given date.",
)
async def get_latest_cif_prior(file_service: FileServiceDep, protein_id: IDCheckDep, date: dt):
    log.info(f"Received request for latest cif file with id {protein_id} prior to {date}")
    file = file_service.get_latest_by_id_before_date(protein_id=protein_id, date=date)

    if not file:
        raise FileNotFound(protein_id=protein_id)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_{date}.cif"'}

    return PlainTextResponse(file, headers=headers)


# TODO Decide on best approach to fetch multiple files.
@router.get(
    "/date/{date}",
    name="New CIF files after date",
    description="Returns new CIF files that have versions after given date.",
)
async def get_new_cif_files(file_service: FileServiceDep, date: dt):
    log.info(f"Received request for new cif files after given date {date}")
    files = file_service.get_new_files_after_date(date)

    if not files:
        raise NoFilesAfterDate(date=date)
