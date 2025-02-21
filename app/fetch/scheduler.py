from zoneinfo import ZoneInfo
from requests import get, Response
from urllib.parse import quote_plus

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED, SchedulerEvent
from arrow import utcnow

from app.log import logger as log
from app.services import ProteinService, FileService, FailedFetchService
from app.config import (
    CRON_JOB_DAY,
    PDB_DATA_API_URL,
    PDB_HTTP_FILE_URL,
    PDB_FTP_STATUS_URL,
)
from app.database.database import get_session


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

    query = f'{{entry(entry_id: "{id}"){{ pdbx_audit_revision_history {{major_revision}}}}}}'
    encoded = quote_plus(query)

    log.debug(f"Query string created. {encoded}")
    return encoded


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


def get_list_file(from_date: str, file_name: str) -> list[str]:
    """Fetches file with new, updated or removed entries."""
    log.debug(f"Trying to fetch file with '{file_name}' entries.")
    url = f"{PDB_FTP_STATUS_URL}{from_date}/{file_name}.pdb"
    response = get(url)

    if response.status_code == 200:
        log.debug("File sucessfully fetched.")
        return list(response.text.split())

    log.error(f"No file found for '{file_name}' entries.")
    return []


def process_failed(failed: list[str], failed_fetch_service: FailedFetchService):
    """Store information about failed fetches for future repeat."""
    log.debug("Storing failed entries for later processing.")
    for entry in failed:
        failed_fetch_service.insert_failed_fetch(protein_id=entry[0], error=entry[1])


def get_last_date():
    """Gets last date when files were updated (currently Friday)."""
    today = utcnow()
    last_date = today.shift(weeks=-1, weekday=5).format("YYYYMMDD")
    return last_date


def process_valid(new: bool):
    """Processes added or updated entries based on flag."""
    log.debug(f"Processing {'new' if new else 'modified'} entries.")
    last_date = get_last_date()
    with get_session() as session:
        file_service = FileService(session)
        added = get_list_file(last_date, "added")
        failed = []

        for id in added:
            full_id = f"pdb_0000{id}"
            category = id[1:3]
            version = 1 if new else get_last_version(id=id)
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
    with get_session() as session:
        protein_service = ProteinService(session)
        obsolete = get_list_file(last_date, "obsolete")
        failed = []
        for id in obsolete:
            result = protein_service.deprecate_protein(protein_id=id)
            if not result:
                full_id = f"pdb_0000{id}"
                failed.append((full_id, f"Failure during insertion of new version. {result}"))
        if obsolete:
            log.debug(f"Finished processing obsolete entries with {len(failed)} failures.")

        if failed:
            failed_service = FailedFetchService(session)
            process_failed(failed, failed_service)


def event_listener(event: SchedulerEvent):
    """Event handler for checking event status."""
    if event.code == EVENT_JOB_ERROR:
        log.error(f"Fetching job crashed because of: {event.exception}\n{event.traceback}")
    elif event.code == EVENT_JOB_EXECUTED:
        log.info("Fetching job was sucessfuly completed.")
    elif event.code == EVENT_JOB_MISSED:
        log.debug("Fetching job missed it's planned execution. It will be re-executed at next available time.")


def get_scheduler():
    """Creates and configures a new scheduler and returns in."""
    log.debug(f"Creating background task with day of week {CRON_JOB_DAY}.")
    scheduler = BackgroundScheduler()

    CET = ZoneInfo("Europe/Prague")
    trigger = CronTrigger(day_of_week=CRON_JOB_DAY, hour=0, minute=0, timezone=CET)
    # trigger = CronTrigger(hour="*", minute="*")
    scheduler.add_job(
        func=process_added, trigger=trigger, replace_existing=True, id="fetch_pdb_job", coalesce=True, max_instances=1
    )
    scheduler.add_job(
        func=process_modified,
        trigger=trigger,
        replace_existing=True,
        id="fetch_pdb_job",
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_job(
        func=process_obsolete,
        trigger=trigger,
        replace_existing=True,
        id="fetch_pdb_job",
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_listener(event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_MISSED | EVENT_JOB_ERROR)

    log.debug("Background task created.")
    return scheduler
