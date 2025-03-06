from requests import get
import concurrent.futures as cf
from math import ceil
from datetime import datetime as dt
from time import sleep
import logging

from app.log import logger as log
from app.config import WORKER_LIMIT, PDB_SEARCH_API_LIMIT
from app.fetch.common import get_last_version, get_search_url, get_file_url, get_file, get_full_id
from app.services import ProteinService, FileService
from app.database.database import get_session
from app.database.models.file import InsertFile


def fetch_ids(start: int, limit: int) -> list[str]:
    """Fetches a list of ids based on start and limit.

    Parameters:
        start: sequence start
        limit: number of ids
    Return:
        list[str]
    """

    url = get_search_url(start=start, limit=limit)

    response = get(url)

    if response.status_code == 200:
        return response.json()


def insert_files(files: list[InsertFile]) -> None:
    """Inserts multiple new file entries at once."""

    with get_session() as session:
        protein_service = ProteinService(session)
        file_service = FileService(session)

        ids = [file.protein_id for file in files]
        protein_service.bulk_insert_new_proteins(ids=ids)

        file_service.bulk_insert_new_files(files)


def fetch_files(total: int) -> None:
    """Main function of a worker process.

    Fetches IDs and corresponding latest file entry. Inserts files into database.

    Parameters:
        total: total number of ids to work with
    Returns:
        None
    """
    log.debug("Entry fetching stareted.")

    logging.getLogger("requests").setLevel(logging.WARNING)

    starts = [x for x in range(0, total, PDB_SEARCH_API_LIMIT)]
    log.debug(f"Created range starts: {starts}")
    total_processed = 0
    for start in starts:
        url = get_search_url(start=start, limit=PDB_SEARCH_API_LIMIT)
        response = get(url)

        if response.status_code == 200:
            if "result_set" in (formatted := response.json()):
                ids = [entry["identifier"] for entry in formatted["result_set"]]
                log.debug(f"Received {len(ids)} ids: ")

                with cf.ThreadPoolExecutor(max_workers=100) as executor:
                    id_to_versions = dict(zip(ids, executor.map(get_last_version, ids)))

                file_urls = {}
                for id in ids:
                    version = id_to_versions[id]
                    full_id = get_full_id(id)
                    file_urls[full_id] = get_file_url(id, version)
                with cf.ThreadPoolExecutor(max_workers=100) as executor:
                    id_to_data = dict(zip(file_urls.keys(), executor.map(get_file, file_urls.values())))

        total_processed += len(ids)
        log.debug(f"Processed {total_processed} so far.")

        # DO NOT DELETE!!!
        sleep(5)  # Required to avoid 'Too many requests' error
        # DO NOT DELETE!!!

    log.debug("Entry fetching finished.")
    logging.getLogger("requests").setLevel(logging.DEBUG)


def get_linspace(total: int):
    "Helper method to calculate step and starts for each worker."

    step = int(ceil(total / WORKER_LIMIT))
    starts = (0 + i * step for i in range(WORKER_LIMIT))

    return step, starts


def run():
    """Creates and starts child processes for fetching file data."""
    log.info("Beggining fetch of all PDB entries.")
    url = get_search_url(start=0, limit=0)

    response = get(url)

    if response.status_code == 200:
        total = response.json()["total_count"]
        log.debug(f"Total number of entries: {total}")
        fetch_files(total)
    else:
        log.error(f"Received unexpected status code: {response.status_code}")


if __name__ == "__main__":
    run()
