"""Main application module for the PDB Mirror API.

This module initializes and configures the FastAPI application, sets up database connections,
and manages the application lifecycle including startup and shutdown events.
"""

from contextlib import asynccontextmanager

from psycopg2 import OperationalError
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from app.log import log as log
from app.config import API_PATH
from app.api.main import api_router
from app.database.database import create_db_and_tables, init_flag_data
from app.fetch.scheduler import scheduler

router = APIRouter()
router.include_router(api_router, prefix=API_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application lifecycle events.

    This function handles startup and shutdown events for the FastAPI application.
    It initializes the database, creates necessary tables, and manages the scheduler.

    Args:
        app: The FastAPI application instance.

    Returns:
        None: This is an async context manager that returns control back to the application.

    Raises:
        OperationalError: If there's an error creating database tables.
    """
    try:
        create_db_and_tables()
        init_flag_data()
    except OperationalError as e:
        log.error(f"An operational error occured white creating tables: {e.pgcode}")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="PDB Mirror 1.0 API",
    contact={"name": "Ján Kučera"},
    redoc_url=None,
    docs_url="/",
    version="beta",
    swagger_ui_parameters={"syntaxHighlight": False, "defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
