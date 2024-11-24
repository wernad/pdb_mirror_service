from fastapi import APIRouter

router = APIRouter()


# TODO Add service and repo for database.
@router.get(
    "/{protein_id}/latest",
    name="Latest CIF",
    description="Returns latest version of CIF file for given protein, if it exists.",
)
async def get_latest_cif(): ...


@router.get(
    "/{protein_id}/{version}",
    name="CIF at version",
    description="Returns specific version of CIF file for given protein, if version and protein exist.",
)
async def get_cif_at_version(): ...
