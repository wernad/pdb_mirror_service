from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    SchedulerEvent,
)

from app.services import ProteinService, FileService, FailedFetchService
from app.database.database import db_context
from app.fetch.utils import (
    fetch_file_at_version,
    get_last_version,
    get_full_id,
    get_last_date,
    get_list_file,
)
from app.log import log as log


def process_failed(failed: list[str], failed_fetch_service: FailedFetchService):
    """Store information about failed fetches for future repeat."""
    log.debug("Storing failed entries for later processing.")
    for entry in failed:
        failed_fetch_service.insert_failed_fetch(protein_id=entry[0], error=entry[1])


# TODO rewrite to use futures and bulk.
def process_valid(new: bool):
    """Processes added or updated entries based on flag."""
    log.debug(f"Processing {'new' if new else 'modified'} entries.")
    last_date = get_last_date()
    file_name = "added" if new else "removed"
    added = get_list_file(last_date, file_name)

    with db_context() as session:
        file_service = FileService(session)
        failed = []

        for id in added:
            full_id = get_full_id(id)
            version = 1 if new else get_last_version(id=id)

            file, error = fetch_file_at_version(full_id, version)

            if error:
                failed.append((full_id, f"Fetch error: {error} "))
            else:
                result = file_service.insert_new_version(
                    protein_id=full_id, file=file, version=version
                )
                if not result:
                    failed.append((full_id, f"Insert error: {result}"))

        if added:
            log.debug(f"Finished processing new entries with {len(failed)} failures.")

        if failed:
            failed_service = FailedFetchService(session)
            process_failed(failed, failed_service)


def process_added() -> None:
    """Wrapper for processing newly added entries."""
    log.debug("Processing new entries.")
    process_valid(new=True)


def process_modified() -> None:
    """Wrapper for processing updated entries."""
    log.debug("Processing updated entries.")
    process_valid(new=False)


def process_obsolete() -> None:
    """Handles processing of removed entries."""
    log.debug("Processing obsolete entries.")
    last_date = get_last_date()
    obsolete = get_list_file(last_date, "obsolete")

    with db_context() as session:
        protein_service = ProteinService(session)
        failed = []

        for id in obsolete:
            full_id = get_full_id(id)
            result = protein_service.deprecate_protein(protein_id=full_id)

            if not result:
                failed.append((full_id, f"Insert error. {result}"))

        if obsolete:
            log.debug(
                f"Finished processing obsolete entries with {len(failed)} failures."
            )

        if failed:
            failed_service = FailedFetchService(session)
            process_failed(failed, failed_service)


def event_listener(event: SchedulerEvent):
    """Event handler for checking event status."""
    if event.code == EVENT_JOB_ERROR:
        log.error(
            f"Fetching job crashed because of: {event.exception}\n{event.traceback}"
        )
    elif event.code == EVENT_JOB_EXECUTED:
        log.info("Fetching job finished.")
    elif event.code == EVENT_JOB_MISSED:
        log.debug(
            "Fetching job missed it's planned execution. It will be re-executed at next planned date."
        )
