from datetime import datetime as dt
import json
from requests import Response, get
from urllib.parse import quote_plus
import multiprocessing as mp

from arrow import utcnow
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.log import logger as log
from app.api.dependencies import FileServiceDep, FailedFetchServiceDep, IDCheckDep, ProteinServiceDep
from app.api.exceptions import FileNotFound, FileVersionNotFound, NoFilesAfterDate
from app.config import (
    PDB_SEARCH_API_URL,
    PDB_DATA_API_URL,
    PDB_SEARCH_API_LIMIT,
    PDB_HTTP_FILE_URL,
    PDB_FTP_STATUS_URL,
)

router = APIRouter()


def get_graphql_query(id: str) -> str:
    """Helper method to create url encoded string for Data API."""
    log.debug(f"Generating GraphQL query string for id {id}")

    query = f'{{entry(entry_id: "{id}"){{ pdbx_audit_revision_history {{major_revision}}}}}}'
    encoded = quote_plus(query)

    log.debug(f"Query string created. {encoded}")
    return encoded


def get_search_query(attribute: str, start: int = 0, limit: int = 1000) -> str:
    """Helper method to create a url encoded string for Search API."""
    log.debug(f"Creating search query string with these params: {attribute=}, {start=}, {limit=}")
    params = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": attribute,
                "operator": "range",
                "value": {"from": "now-1w", "include_lower": True},
            },
        },
        "request_options": {"paginate": {"start": start, "rows": limit}},
        "return_type": "entry",
    }

    json_params = json.dumps(params)
    encoded = quote_plus(json_params)
    log.debug(f"Query string created. {encoded}")
    return encoded


def get_error_message(response: Response) -> str:
    """Extracts error message if any given, otherwise returns plain text."""
    log.debug("Extractng error message.")
    try:
        message = response.json()
    except Exception as _:
        message = response.text

    return message


def get_last_version(id: str) -> int | None:
    """Fetches latest version number of given file ID."""
    log.debug(f"Fetching latest version of a file with ID {id}.")

    query = get_graphql_query(id)

    url = f"{PDB_DATA_API_URL}?query={query}"
    response = get(url)

    if response.status_code == 200:
        body = response.json()
        version = body["data"]["entry"]["pdbx_audit_revision_history"][-1]["major_revision"]
        log.debug(f"File {id} - latest version: {version}.")
        return version

    message = get_error_message(response)
    log.debug(f"No version retrieved for id {id} - error: {message}")
    return None


def get_list_file(from_date: str, file_name: str) -> list[str] | None:
    """Fetches file with new, updated or removed entries."""
    log.debug(f"Fetching file with '{file_name}' entries.")
    url = f"{PDB_FTP_STATUS_URL}{from_date}/{file_name}.pdb"

    response = get(url)
    if response.status_code == 200:
        log.debug("File sucessfully fetched.")
        return list(response.text.split())

    log.error(f"No '{file_name}' file received.")
    return None


def process_added(file_service: FileServiceDep, date_from: str) -> None:
    """Handles processing of newly added entries."""
    log.debug("Processing new entries.")

    added = get_list_file(date_from, "added")
    failed = []

    for id in added:
        full_id = f"pdb_0000{id}"
        category = id[1:3]
        version = 1  # New entry -> first version.
        file_name = f"{full_id}_xyz_v{version}.cif.gz"
        url = f"{PDB_HTTP_FILE_URL}/{category}/{full_id}/{file_name}"
        response = get(url)

        if response.status_code == 200:
            body = response.content
            result = file_service.insert_new_version(protein_id=full_id, file=body, version=version)

            if not result:
                failed.append((full_id, f"Failure during insertion of new version. {result}"))
        else:
            failed.append((full_id, f"Received error code {response.status_code} during file fetch"))

    log.debug(f"Finished processing new entries with {len(failed)} failures.")
    return failed


def process_modified(file_service: FileServiceDep, date_from: str) -> None:
    """Handles processing of updated entries."""
    log.debug("Processing updated entries.")
    modified = get_list_file(date_from, "modified")

    failed = []
    for id in modified:
        full_id = f"pdb_0000{id}"
        category = id[1:3]
        version = get_last_version(id)
        file_name = f"{full_id}_xyz_v{version}.cif.gz"
        url = f"{PDB_HTTP_FILE_URL}/{category}/{full_id}/{file_name}"
        response = get(url)

        if response.status_code == 200:
            body = response.content
            result = file_service.insert_new_version(protein_id=full_id, file=body, version=version)

            if not result:
                failed.append((full_id, f"Failure during insertion of new version. {result}"))
        else:
            failed.append((full_id, f"Received error code {response.status_code} during file fetch"))
    log.debug(f"Finished processing updated entries with {len(failed)} failures.")
    return failed


def process_obsolete(protein_service: ProteinServiceDep, date_from: str) -> None:
    """Handles processing of removed entries."""
    log.debug("Processing obsolete entries.")
    obsolete = get_list_file(date_from, "obsolete")
    failed = []
    for id in obsolete:
        result = protein_service.deprecate_protein(protein_id=id)
        if not result:
            full_id = f"pdb_0000{id}"
            failed.append((full_id, f"Failure during insertion of new version. {result}"))
    log.debug(f"Finished processing obsolete entries with {len(failed)} failures.")
    return failed


def process_failed(failed: list[str], failed_fetch_service: FailedFetchServiceDep):
    """Store information about failed fetches for future repeat."""
    log.debug("Storing failed entries for later processing.")
    for entry in failed:
        failed_fetch_service.insert_failed_fetch(protein_id=entry[0], error=entry[1])


# TODO Multiprocessing
def process_latest_changes(
    protein_service: ProteinServiceDep,
    file_service: FileServiceDep,
    failed_fetch_service: FailedFetchServiceDep,
    date_from: str,
):
    """Downloads files with list of new/modified/removed entries and processes them accordingly."""
    failed = []
    failed.append(process_added(file_service, date_from))
    failed.append(process_modified(file_service, date_from))
    failed.append(process_obsolete(protein_service, date_from))

    log.debug(f"Processing ended, updating failed entries with {len(failed)} new rows.")

    process_failed(failed, failed_fetch_service)


@router.get("/ping")
async def ping() -> None:
    """Endpoint to test connection."""
    return None


# TODO rewrite to use Search API.
# removed rcsb_accession_info.deposit_date
# modified rcsb_accession_info.revision_date
@router.get("/")
async def get_files(
    protein_service: ProteinServiceDep, file_service: FileServiceDep, failed_fetch_service: FailedFetchServiceDep
):
    # today = pendulum.now()
    # last_saturday = today.previous(pendulum.FRIDAY).strftime("%Y%m%d")
    today = utcnow()
    last_saturday = today.shift(weeks=-1, weekday=5).format("YYYYMMDD")
    process_latest_changes(protein_service, file_service, failed_fetch_service, last_saturday)

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
