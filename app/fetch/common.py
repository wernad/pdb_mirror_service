from urllib.parse import quote_plus
from requests import Response, get
import json

from app.log import logger as log
from app.config import PDB_DATA_API_URL, PDB_HTTP_FILE_URL, PDB_SEARCH_API_URL


def get_full_id(id: str):
    """Returns 12-character id of given 4-character id."""
    return f"pdb_0000{id}"


def get_error_message(response: Response) -> str:
    """Extracts error message if any given, otherwise returns plain text."""
    log.debug("Extractng error message.")
    try:
        message = response.json()
    except Exception as _:
        message = response.text

    return message


def get_graphql_query(id: str) -> str:
    """Helper method to create url encoded string for Data API."""
    log.debug(f"Generating GraphQL query string for id {id}")

    query = f'{{entry(entry_id: "{id}"){{pdbx_audit_revision_history{{major_revision}}}}}}'
    encoded = quote_plus(query)

    log.debug(f"Query string created. {encoded}")
    return encoded


def get_search_url(start: int = 0, limit: int = 1000) -> str:
    """Helper method to create a url encoded string for Search API."""
    log.debug(f"Creating search query string with these params: {start=}, {limit=}")
    params = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {"attribute": "rcsb_accession_info.initial_release_date", "operator": "exists"},
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


def get_all_versions(id: str) -> set[int]:
    """Fetches all versions of given structure, if any."""

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


def fetch_file_at_version(id: str, version: str):
    """Fetches file with given id at given version.

    Parameters:
        id: 12-character structure id
        version: version to fetch
    Returns:
        bytes
    """

    category = id[1:3]
    file_name = f"{id}_xyz_v{version}.cif.gz"
    url = f"{PDB_HTTP_FILE_URL}{category}/{id}/{file_name}"
    response = get(url)

    if response.status_code == 200:
        body = response.content
        return body, None
    return None, response.status_code
