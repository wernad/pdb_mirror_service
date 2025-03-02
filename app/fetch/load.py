from requests import get
import concurrent.futures as cf
import multiprocessing as mp
from math import ceil
from datetime import datetime as dt

from app.log import logger as log
from app.config import WORKER_LIMIT, PDB_SEARCH_API_LIMIT
from app.fetch.common import get_all_versions, get_search_url, get_graphql_query, get_file_url, get_files, get_full_id
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


# TODO fix too many requests error, possibly remove multiprocessing.
def task(worker_id: int, start: int, end: int) -> None:
    """Main function of a worker process.

    Fetches IDs, versions and files. Inserts fetched data into database.

    Parameters:
        from_: start of range
        chunk_size: how many entries to fetch
    Returns:
        None
    """
    log.debug(f"Starting worker {worker_id} with params: {start=}, {end=}")

    starts = [x for x in range(start, end, PDB_SEARCH_API_LIMIT)]
    log.debug(f"Range starts for worker {worker_id}: {starts}")
    for start in starts:
        url = get_search_url(start=start, limit=PDB_SEARCH_API_LIMIT)
        response = get(url)

        if response.status_code == 200:
            log.debug("Ids received, starting file fetching.")
            if "result_set" in (formatted := response.json()):
                failed = []  # TODO add failed handling after updating failed table with new column.

                ids = [entry["identifier"] for entry in formatted["result_set"]]
                graph_urls = {}
                for id in ids:
                    graph_urls[id] = get_graphql_query(id)

                with cf.ThreadPoolExecutor(max_workers=100) as executor:
                    id_to_versions = dict(zip(graph_urls.keys(), executor.map(get_all_versions, graph_urls.values())))

                with cf.ThreadPoolExecutor(max_workers=100) as executor:
                    file_urls = {}
                    for id in ids:
                        versions = id_to_versions[id]
                        full_id = get_full_id(id)
                        file_urls[full_id] = []
                        for version in versions:
                            file_urls[full_id].append(get_file_url(full_id, version))
                    id_to_data = dict(zip(file_urls.keys(), executor.map(get_files, file_urls.values())))
                    files_to_insert = []
                    for id, data in id_to_data:
                        for idx, bytes_entry in enumerate(data):
                            version = idx + 1
                            new_file = InsertFile(
                                protein_id=id, timestamp=dt.today(), version=version, file=bytes_entry
                            )
                            files_to_insert.append(new_file)
                    insert_files(files_to_insert)

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
