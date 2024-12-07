from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.api.dependencies import FileServiceDep
from app.api.exceptions import FileNotFound, FileVersionNotFound

router = APIRouter()


@router.get(
    "/{protein_id}/latest",
    name="Latest CIF",
    description="Returns latest version of CIF file for given protein, if it exists.",
)
async def get_latest_cif(file_service: FileServiceDep, protein_id: str):
    file = file_service.get_latest_by_protein_id(protein_id=protein_id)

    if not file:
        raise FileNotFound(protein_id)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}.cif"'}

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/version/{version}",
    name="CIF at version",
    description="Returns specific version of CIF file for given protein, if version and protein exist.",
)
async def get_cif_at_version(file_service: FileServiceDep, protein_id: str, version: int):
    print("###")
    file = file_service.get_by_version_and_protein_id(protein_id=protein_id, version=version)

    if not file:
        raise FileVersionNotFound(protein_id=protein_id, version=version)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_v{version}.cif"'}

    return PlainTextResponse(file, headers=headers)


@router.get(
    "/{protein_id}/date/{date}",
    name="Latest CIF prior to date",
    description="Returns latest of CIF file for given protein before given date.",
)
async def get_latest_cif_prior(file_service: FileServiceDep, protein_id: str, date: datetime):
    print("@@@")
    file = file_service.get_latest_by_id_before_date(protein_id=protein_id, date=date)

    if not file:
        raise FileNotFound(protein_id=protein_id)

    headers = {"Content-Disposition": f'attachment; filename="pdb_mirror_{protein_id}_{date}.cif"'}

    return PlainTextResponse(file, headers=headers)
