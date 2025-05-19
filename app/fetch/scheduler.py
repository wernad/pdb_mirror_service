"""Scheduler module for managing periodic PDB data synchronization tasks.

This module implements a singleton scheduler that manages periodic jobs for fetching
and processing PDB data updates, including added, modified, and obsolete entries.
"""

from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
)

from app.log import log as log
from app.config import (
    CRON_JOB_DAY,
)
from app.fetch.jobs import (
    process_added,
    process_modified,
    process_obsolete,
    event_listener,
)

__all__ = ["scheduler"]


class Singleton(type):
    """Metaclass for implementing the Singleton pattern.

    This metaclass ensures that only one instance of a class is created
    and provides access to that instance.
    """

    def __init__(self, *args, **kwargs):
        self._instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Creates or returns the singleton instance of the class.

        Returns:
            object: The singleton instance of the class.
        """
        if self._instance is None:
            log.debug("Creating a new singleton instance of Scheduler.")
            self._instance = super().__call__(*args, **kwargs)
        else:
            log.debug("Scheduler exists, returning current instance instead.")
        return self._instance


class Scheduler(metaclass=Singleton):
    """Scheduler class for managing periodic PDB data synchronization jobs.

    This class implements a singleton pattern to ensure only one scheduler instance
    exists throughout the application. It manages jobs for processing added, modified,
    and obsolete PDB entries on a scheduled basis.
    """

    def __init__(self):
        """Initializes the scheduler with background jobs."""
        super().__init__()
        self.scheduler = self._create_scheduler()
        self.value = None

    def _create_scheduler(self):
        """Creates and configures a new scheduler instance.

        Returns:
            BackgroundScheduler: A configured scheduler instance with jobs for
                processing PDB data updates.
        """
        log.debug(
            f"Creating background scheduler set to day of the week: {CRON_JOB_DAY}."
        )
        scheduler = BackgroundScheduler()

        CET = ZoneInfo("Europe/Prague")
        trigger = CronTrigger(day_of_week=CRON_JOB_DAY, hour=0, minute=0, timezone=CET)
        scheduler.add_job(
            func=process_added,
            trigger=trigger,
            replace_existing=True,
            id="fetch_added",
            coalesce=True,
            max_instances=1,
        )
        scheduler.add_job(
            func=process_modified,
            trigger=trigger,
            replace_existing=True,
            id="fetch_modified",
            coalesce=True,
            max_instances=1,
        )
        scheduler.add_job(
            func=process_obsolete,
            trigger=trigger,
            replace_existing=True,
            id="fetch_obsolete",
            coalesce=True,
            max_instances=1,
        )
        scheduler.add_listener(
            event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_MISSED | EVENT_JOB_ERROR
        )

        log.debug("Scheduler with jobs created.")

        return scheduler

    def start(self):
        """Starts the scheduler and all configured jobs."""
        self.scheduler.start()

    def shutdown(self):
        """Shuts down the scheduler and all running jobs."""
        self.scheduler.shutdown()

    def get_jobs(self):
        """Returns all jobs configured in the scheduler.

        Returns:
            A list of all jobs configured in the scheduler.
        """
        return self.scheduler.get_jobs()


scheduler = Scheduler()
