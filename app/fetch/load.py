"""Data loading module for PDB entries.

This module provides functions for fetching and loading PDB entries into the database,
including parallel processing capabilities and error handling.
"""

from requests import get
import concurrent.futures as cf
from math import ceil
from datetime import datetime as dt
from time import sleep
import logging

from app.log import log as log
from app.config import WORKER_LIMIT, PDB_SEARCH_API_LIMIT
from app.fetch.utils import (
    get_last_version,
    get_search_url,
    get_file_url,
    get_file,
    get_full_id,
)
from app.services import ProteinService, FileService
from app.database.database import db_context
from app.database.models import FileInsert, ChangeInsert, Operations


def fetch_ids(start: int, limit: int) -> list[str]:
    """Fetches a list of PDB IDs based on start and limit parameters.

    Args:
        start: The starting index for pagination.
        limit: The maximum number of IDs to fetch.

    Returns:
        List of PDB IDs if successful, None if the request fails.
    """
    url = get_search_url(start=start, limit=limit)

    response = get(url)

    if response.status_code == 200:
        return response.json()

    log.error(f"Received unexpected status code: {response.status_code}")

    return None


def get_latest_versions(ids: list[str]) -> dict:
    """Returns dictionary of latest versions of each protein ID.

    Args:
        ids: List of PDB IDs to fetch versions for.

    Returns:
        Dictionary mapping PDB IDs to their latest version numbers.
    """
    with cf.ThreadPoolExecutor(max_workers=WORKER_LIMIT) as executor:
        id_to_version = dict(zip(ids, executor.map(get_last_version, ids)))

    return id_to_version


def get_file_urls(ids: list[str], id_to_version: dict) -> dict:
    """Returns url for fetching latest file for each protein ID.

    Args:
        ids: List of PDB IDs.
        id_to_version: Dictionary mapping PDB IDs to their versions.

    Returns:
        Dictionary mapping PDB IDs to their file URLs.
    """
    file_urls = {}
    for id in ids:
        version = id_to_version[id]
        file_urls[id] = get_file_url(id, version)

    return file_urls


def fetch_files(file_urls: dict, id_to_version: dict) -> tuple:
    """Fetches files from given urls and returns SQLModel objects for insertion.

    Args:
        file_urls: Dictionary mapping PDB IDs to their file URLs.
        id_to_version: Dictionary mapping PDB IDs to their versions.

    Returns:
        A tuple containing:
            - list[FileInsert]: List of file objects to insert
            - list[ChangeInsert]: List of change objects to insert
            - list[str]: List of failed PDB IDs
    """
    with cf.ThreadPoolExecutor(max_workers=WORKER_LIMIT) as executor:
        id_to_data = dict(
            zip(file_urls.keys(), executor.map(get_file, file_urls.values()))
        )

    failed = []
    files_to_insert = []
    changes_to_insert = []

    for id, data in id_to_data.items():
        if data:
            full_id = get_full_id(id)
            version = id_to_version[id]

            new_file = FileInsert(protein_id=full_id, version=version, file=data)
            files_to_insert.append(new_file)

            new_change = ChangeInsert(
                file_id=0,  # placeholder
                protein_id=full_id,
                operation_flag=Operations.ADDED.value,
                timestamp=dt.now(),
            )
            changes_to_insert.append(new_change)
        else:
            failed.append(id)

    return files_to_insert, changes_to_insert, failed


def insert_files(files: list[FileInsert], changes: list[ChangeInsert]) -> None:
    """Inserts multiple new file entries at once.

    Args:
        files: List of file objects to insert.
        changes: List of change objects to insert.
    """
    with db_context() as session:
        protein_service = ProteinService(session)
        file_service = FileService(session)

        ids = [file.protein_id for file in files]
        protein_service.bulk_insert_new_proteins(ids=ids)

        batch_size = 100
        for i in range(0, len(files), batch_size):
            batch_files = files[i : i + batch_size]
            batch_changes = changes[i : i + batch_size] if i < len(changes) else []
            file_service.bulk_insert_new_files(batch_files, batch_changes)


def fetch_all(start: int, total: int) -> None:
    """Fetches IDs and corresponding latest file entries and stores them in database.

    Uses threads to speed up the fetching but requires explicit timeout after given batch,
    to avoid overwhelming PDB APIs.

    Args:
        start: The starting index for fetching.
        total: Total number of IDs to process.
    """
    log.debug("Entry fetching stareted.")

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    starts = [x for x in range(start, total, PDB_SEARCH_API_LIMIT)]
    log.debug(f"Created range starts: {starts}")
    total_processed = 0
    total_failed = 0
    for start in starts:
        url = get_search_url(start=start, limit=PDB_SEARCH_API_LIMIT)
        response = get(url)
        if response.status_code == 200 and "result_set" in (
            formatted := response.json()
        ):
            ids = [entry["identifier"] for entry in formatted["result_set"]]
            log.debug(f"Received {len(ids)} ids.")

            id_to_version = get_latest_versions(ids)
            file_urls = get_file_urls(ids, id_to_version)

            files_to_insert, changes_to_insert, failed_batch = fetch_files(
                file_urls, id_to_version
            )

            insert_files(files_to_insert, changes_to_insert)

            total_processed += len(ids)
            total_failed += len(failed_batch)
            if failed_batch:
                log.debug(f"Number of failed ids: {len(failed_batch)}")
                with open("failed.txt", "a+") as file:
                    file.write("\n".join([x for x in failed_batch]))
        log.debug(
            f"Total processed: {total_processed} -- Total failed: {total_failed}."
        )

        # DO NOT DELETE!!!
        sleep(5)  # Required to avoid 'Too many requests' error
        # DO NOT DELETE!!!

    log.debug("Entry fetching finished.")

    logging.getLogger("requests").setLevel(logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)


def get_linspace(total: int):
    """Helper method to calculate step and starts for each worker.

    Args:
        total: Total number of items to process.

    Returns:
        A tuple containing:
            - Step size for each worker
            - Generator of start indices for each worker
    """
    step = int(ceil(total / WORKER_LIMIT))
    starts = (0 + i * step for i in range(WORKER_LIMIT))

    return step, starts


def run(start: int | None):
    """Creates and starts child processes for fetching file data.

    Args:
        start: Starting index for fetching. If None, starts from 0.
    """
    log.info("Beggining fetch of all PDB entries.")
    ids_data = fetch_ids(start=0, limit=0)

    if ids_data is not None:
        total = ids_data["total_count"]
        log.debug(f"Total number of entries: {total}")
        actual_start = start if start else 0
        fetch_all(start=actual_start, total=total)


if __name__ == "__main__":
    run()
