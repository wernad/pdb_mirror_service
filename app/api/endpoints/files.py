from datetime import datetime as dt

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.log import logger as log
from app.api.dependencies import FileServiceDep, IDCheckDep, ProteinServiceDep
from app.api.exceptions import FileNotFound, FileVersionNotFound, NoFilesAfterDate

router = APIRouter()


@router.get("/ping")
async def ping() -> None:
    """Endpoint to test connection."""
    return None


@router.get(
    "/{protein_id}/latest",
    name="Latest CIF",
    description="Returns latest version of CIF file for given protein, if it exists.",
)
async def get_latest_cif(file_service: FileServiceDep, protein_id: IDCheckDep):
    log.info(f"Received request for latest cif file with id {protein_id}")
    file = file_service.get_latest_by_protein_id(protein_id=protein_id)

    if not file:
        log.error(f"File with id {protein_id} not found.")
        raise FileNotFound(protein_id)

    headers = {
        "Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}.cif"'
    }

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/version/{version}",
    name="CIF at version",
    description="Returns specific version of CIF file for given protein, if version and protein exist.",
)
async def get_cif_at_version(
    file_service: FileServiceDep, protein_id: IDCheckDep, version: int
):
    log.info(f"Received request for cif file with id {protein_id} at version {version}")
    file = file_service.get_by_version_and_protein_id(
        protein_id=protein_id, version=version
    )

    if not file:
        log.error(f"File for id {protein_id} at version {version} not found.")
        raise FileVersionNotFound(protein_id=protein_id, version=version)

    headers = {
        "Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_v{version}.cif"'
    }

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/date/{date}",
    name="Latest CIF prior to date",
    description="Returns latest CIF file for given protein before given date.",
)
async def get_latest_cif_prior(
    file_service: FileServiceDep, protein_id: IDCheckDep, date: dt
):
    log.info(
        f"Received request for latest cif file with id {protein_id} prior to {date}"
    )
    file = file_service.get_latest_by_id_before_date(protein_id=protein_id, date=date)

    if not file:
        raise FileNotFound(protein_id=protein_id)

    headers = {
        "Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_{date}.cif"'
    }

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/date/{date}",
    name="New IDs after date",
    description="Returns IDs of entries with new files after given date.",
)
async def get_new_cif_files(file_service: ProteinServiceDep, date: dt):
    log.info(f"Received request for new cif files after given date {date}")
    files = file_service.get_protein_ids_after_date(date)

    if not files:
        raise NoFilesAfterDate(date=date)
