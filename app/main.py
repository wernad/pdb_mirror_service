from fastapi import FastAPI, APIRouter

from app.config import API_PATH
from app.api.main import api_router
from app.database.database import create_db_and_tables
from psycopg2 import OperationalError

router = APIRouter()
router.include_router(api_router, prefix=API_PATH)

app = FastAPI(
    title="PDB Mirror 0.1 API",
    contact={"name": "Ján Kučera"},
    redoc_url=None,
    docs_url="/",
    version="beta",
    swagger_ui_parameters={"syntaxHighlight": False, "defaultModelsExpandDepth": -1},
)

app.include_router(router)


@app.on_event("startup")
def on_startup():
    try:
        print("Creating database and tables.")
        create_db_and_tables()
    except OperationalError as e:
        print(f"An operational error occured white creating tables: {e.pgcode}")
