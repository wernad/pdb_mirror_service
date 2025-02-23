from requests import get
import multiprocessing as mp
from math import ceil

from app.log import logger as log
from app.config import WORKER_LIMIT, PDB_SEARCH_API_LIMIT, BYTE_LIMIT
from app.fetch.common import get_all_versions, get_search_url, fetch_file_at_version
from app.services import ProteinService, FileService
from app.database.database import get_session


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


def insert_files(files: list[tuple]) -> None:
    """Inserts multiple new file entries at once."""

    ids = [x[0] for x in files]
    with get_session() as session:
        protein_service = ProteinService(session)
        file_service = FileService(session)

        protein_service.bulk_insert_new_proteins(ids=ids)

        file_service.bulk_insert_new_files(files)


def task(worker_id: int, from_: int, chunk_size: int) -> None:
    """Main function of a worker process.

    Fetches IDs, versions and files. Inserts fetched data into database.

    Parameters:
        from_: start of range
        chunk_size: how many entries to fetch
    Returns:
        None
    """
    log.debug(f"Starting worker {worker_id} with params: {from_=}, {chunk_size=}")

    starts = [x for x in range(from_, from_ + chunk_size, PDB_SEARCH_API_LIMIT)]
    for start in starts:
        url = get_search_url(start=start, limit=PDB_SEARCH_API_LIMIT)
        response = get(url)

        if response.status_code == 200:
            log.debug("Ids received, starting file fetching.")
            if "result_set" in (formatted := response.json()):
                files = []
                failed = []
                total_size = 0

                ids = [entry["identifier"] for entry in formatted["result_set"]]
                for id in ids:
                    log.debug(f"Worker {worker_id} - fetching structure id {id}")
                    versions = get_all_versions(id=id)

                    for version in versions:
                        file, error = fetch_file_at_version(id=id, version=version)
                        if file:
                            total_size += len(file)
                            files.append((id, version, file))
                            if total_size > BYTE_LIMIT:
                                insert_files(files)
                                files = []
                                total_size = 0
                        else:
                            failed.append(id)
                if files:
                    insert_files(files)
            else:
                return
    log.debug(f"Worker {worker_id} finished.")


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
        total = 1000  # TODO testing only
        step, starts = get_linspace(total)

        log.debug(f"Creating workers with params: {step=}, {starts=}.")
        processes = []
        for idx, start in enumerate(starts):
            end = start + step
            p = mp.Process(target=task, args=(idx, start, end))
            p.start()
            processes.append(p)

        log.debug("Waiting for workers to finish.")
        for p in processes:
            p.join()

    else:
        log.error(f"Received unexpected status code: {response.status_code}")


if __name__ == "__main__":
    run()
