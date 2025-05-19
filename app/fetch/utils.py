"""Utility functions for PDB data fetching and processing.

This module provides helper functions for interacting with the PDB API,
including fetching files, managing versions, and handling API responses.
"""

from urllib.parse import quote_plus
from arrow import utcnow
from requests import Response, get
from requests.exceptions import ConnectTimeout
import json

from app.log import log as log
from app.config import (
    PDB_DATA_API_URL,
    PDB_FTP_STATUS_URL,
    PDB_HTTP_FILE_URL,
    PDB_SEARCH_API_URL,
)


def get_full_id(id: str):
    """Returns 12-character id of given 4-character id.

    Args:
        id: The 4-character PDB ID.

    Returns:
        str: The 12-character full PDB ID.
    """
    return f"pdb_0000{id.lower()}"


def get_error_message(response: Response) -> str:
    """Extracts error message if any given, otherwise returns plain text.

    Args:
        response: The HTTP response object.

    Returns:
        The error message from the response, either as JSON or plain text.
    """
    log.debug("Extractng error message.")
    try:
        message = response.json()
    except Exception as _:
        message = response.text

    return message


def get_file_url(id: str, version: str) -> str:
    """Create file url based on id and version.

    Args:
        id: The PDB structure ID.
        version: The version number to fetch.

    Returns:
        The complete URL for the requested file.
    """
    log.debug(f"Creating url for file - {id=} {version=}.")
    id = id.lower()
    full_id = get_full_id(id)
    category = id[1:3]
    file_name = f"{full_id}_xyz_v{version}.cif.gz"
    url = f"{PDB_HTTP_FILE_URL}{category}/{full_id}/{file_name}"
    log.debug(f"Created file url: {url}")
    return url


def get_graphql_query(id: str) -> str:
    """Helper method to create url encoded string for Data API.

    Args:
        id: The PDB structure ID.

    Returns:
        The URL-encoded GraphQL query string.
    """
    log.debug(f"Generating GraphQL query string for id {id}")

    query = (
        f'{{entry(entry_id: "{id}"){{pdbx_audit_revision_history{{major_revision}}}}}}'
    )
    encoded = quote_plus(query)

    url = f"{PDB_DATA_API_URL}?query={encoded}"
    return url


def get_search_url(start: int = 0, limit: int = 1000) -> str:
    """Helper method to create a url encoded string for Search API.

    Args:
        start: The starting index for pagination. Defaults to 0.
        limit: The maximum number of results to return. Defaults to 1000.

    Returns:
        The URL-encoded search query string.
    """
    log.debug(f"Creating search query string with these params: {start=}, {limit=}")
    params = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_accession_info.initial_release_date",
                "operator": "exists",
            },
        },
        "request_options": {"paginate": {"start": start, "rows": limit}},
        "return_type": "entry",
    }

    json_params = json.dumps(params)
    encoded = quote_plus(json_params)
    url = f"{PDB_SEARCH_API_URL}?json={encoded}"
    log.debug(f"URL string created. {url}")
    return url


def get_last_version(id: str) -> int | None:
    """Fetches latest version number of given file ID.

    Args:
        id: The PDB structure ID.

    Returns:
        The latest version number if found, None otherwise.
    """
    log.debug(f"Fetching latest version of a file with ID {id}.")

    url = get_graphql_query(id)
    log.debug(f"Query for {id}: {url}")

    response = get(url)
    if response.status_code == 200:
        body = response.json()
        version = body["data"]["entry"]["pdbx_audit_revision_history"][-1][
            "major_revision"
        ]
        log.debug(f"File {id} - latest version: {version}.")
        return version

    message = get_error_message(response)
    log.debug(f"No version retrieved for id {id} - error: {message}")
    return None


def get_all_versions(id: str) -> set[int]:
    """Fetches all versions of given structure, if any.

    Args:
        id: The PDB structure ID.

    Returns:
        Set of all version numbers if found, None otherwise.
    """
    log.debug(f"Fetching all versions of file with ID {id}.")

    query = get_graphql_query(id)

    url = f"{PDB_DATA_API_URL}?query={query}"
    response = get(url)

    if response.status_code == 200:
        body = response.json()
        data = body["data"]["entry"]["pdbx_audit_revision_history"]

        versions = set([x["major_revision"] for x in data])

        log.debug(f"File {id} - versions found: {versions}.")
        return versions

    message = get_error_message(response)
    log.debug(f"No versions retrieved for id {id} - error: {message}")
    return None


def fetch_files(urls: list[str]) -> list[bytes]:
    """Fetches files from given urls.

    Args:
        urls: List of URLs to fetch files from.

    Returns:
        List of file contents as bytes.
    """
    log.debug(f"Fetching {len(urls)} files.")
    files = []

    for url in urls:
        response = get(url)

        if response.status_code == 200:
            files.append(response.content)
    log.debug("Fetching done.")
    return files


def get_file(url: list[str]) -> list[bytes]:
    """Fetches files from given urls with retry logic.

    Args:
        url: List of URLs to fetch files from.

    Returns:
        List of file contents as bytes.
    """
    log.debug(f"Fetching file from url: {url}")
    finished = False
    while not finished:
        try:
            response = get(url)
            code = response.status_code
            if code == 200:
                log.debug("Fetching complete.")
                finished = True
                return response.content
            log.error(f"Unexpected status code {code} for url: {url}")
        except ConnectTimeout as _:
            log.error(f"Connection timed out on url: {url}")

    log.error(f"Fetching failed for url: {url}")


def fetch_file_at_version(id: str, version: str) -> tuple:
    """Fetches file with given id at given version.

    Args:
        id: The 12-character structure ID.
        version: The version number to fetch.

    Returns:
        A tuple containing (file_content, error_code) where file_content is bytes
            and error_code is None if successful, or (None, error_code) if failed.
    """
    category = id[1:3].lower()
    file_name = f"{id}_xyz_v{version}.cif.gz"
    url = f"{PDB_HTTP_FILE_URL}{category}/{id}/{file_name}"
    response = get(url)

    if response.status_code == 200:
        body = response.content
        return body, None
    return None, response.status_code


def get_list_file(from_date: str, file_name: str) -> list[str]:
    """Fetches file with new, updated or removed entries.

    Args:
        from_date: The date to fetch entries from.
        file_name: The type of entries to fetch ('added', 'modified', or 'obsolete').

    Returns:
        List of PDB IDs from the requested file.
    """
    log.debug(f"Trying to fetch file with '{file_name}' entries.")
    url = f"{PDB_FTP_STATUS_URL}{from_date}/{file_name}.pdb"
    response = get(url)

    if response.status_code == 200:
        log.debug("File sucessfully fetched.")
        return list(response.text.split())

    log.error(f"No file found for '{file_name}' entries.")
    return []


def get_last_date():
    """Gets last date when files were updated (currently Friday).

    Returns:
        The date string in YYYYMMDD format.
    """
    today = utcnow()
    last_date = today.shift(weeks=-1, weekday=5).format("YYYYMMDD")
    return last_date
