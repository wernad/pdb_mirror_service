from contextlib import asynccontextmanager

from psycopg2 import OperationalError
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from app.log import logger as log
from app.config import API_PATH
from app.api.main import api_router
from app.database.database import create_db_and_tables
from app.fetch.scheduler import get_scheduler

router = APIRouter()
router.include_router(api_router, prefix=API_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        log.debug("Creating database and tables.")
        create_db_and_tables()
        log.debug("Database and tables created successfully.")
    except OperationalError as e:
        log.error(f"An operational error occured white creating tables: {e.pgcode}")

    scheduler = get_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="PDB Mirror 0.1 API",
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
