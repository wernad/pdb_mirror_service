from typing import Annotated
from fastapi import APIRouter, Query
from datetime import datetime as dt

from app.log import log as log
from app.api.dependencies import ProteinServiceDep
from app.database.models import Padding, Operations

router = APIRouter()


@router.get(
    "/total_count",
    name="Total count",
    description="Returns total count of protein entries.",
)
async def get_total_count(protein_service: ProteinServiceDep):
    log.info("Fetching total count of proteins")
    total_count = protein_service.get_total_count()

    return {"total_count": total_count}


@router.get(
    "/all",
    name="All present ids",
    description="Returns list of all protein ids in database.",
)
async def get_all_ids(
    protein_service: ProteinServiceDep, params: Annotated[Padding, Query()]
) -> dict:
    log.info(f"Fetching all ids with parameters:: {params.offset=}, {params.limit=}")
    ids = protein_service.get_all_ids(limit=params.limit, offset=params.offset)
    total_count = protein_service.get_total_count()

    return {"data": ids, "total_count": total_count}


@router.get(
    "/changes/added/{start_date}",
    name="Added ids",
    description="Returns list of protein ids added after given date.",
)
async def get_added_after_date(
    start_date: dt, protein_service: ProteinServiceDep
) -> list:
    result = protein_service.get_changes_after_date(
        start_date=start_date, change=Operations.ADDED
    )

    return result


@router.get(
    "/changes/modified/{start_date}",
    name="Modified ids",
    description="Returns list of protein ids modified after given date.",
)
async def get_modified_after_date(
    start_date: dt, protein_service: ProteinServiceDep
) -> list:
    result = protein_service.get_changes_after_date(
        start_date=start_date, change=Operations.MODIFIED
    )

    return result


@router.get(
    "/changes/obsolete/{start_date}",
    name="Removed ids",
    description="Returns list of protein ids removed after given date.",
)
async def get_removed_after_date(
    start_date: dt, protein_service: ProteinServiceDep
) -> list:
    result = protein_service.get_changes_after_date(
        start_date=start_date, change=Operations.OBSOLETE
    )

    return result
