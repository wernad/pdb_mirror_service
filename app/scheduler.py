from app.log import logger as log
from zoneinfo import ZoneInfo
from requests import get

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED, SchedulerEvent


from app.config import CRON_JOB_DAY, PDB_RSYNC_URL, PDB_HTTP_VIEW_URL


def info_from_path(path: str):
    """Regex extraction of relevant data from given file path."""


# TODO
def get_modified():
    """Fetches current state of modified entries and finds the ones that are less than a week old."""


# TODO
def fetch_new_data():
    """Fetch job for downloading all new cif files from PDB."""
    log.info(f"@@@@ TASK DONE {PDB_RSYNC_URL}")


def event_listener(event: SchedulerEvent):
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

    scheduler.add_job(func=fetch_new_data, trigger=trigger, replace_existing=True, id="fetch_pdb_job", coalesce=True)
    scheduler.add_listener(event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_MISSED | EVENT_JOB_ERROR)

    log.debug("Background task created.")
    return scheduler
