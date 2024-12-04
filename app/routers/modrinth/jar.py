from fastapi import HTTPException, APIRouter
from starlette.responses import RedirectResponse

from app.models.modrinth import Loader
from app.routers.modrinth.pom import validate_and_get_version_for_loader

router = APIRouter()


@router.get("/repository/com/modrinth/{loader}/{project_id_or_slug}/{version_id_or_number}/{filename}.jar",
            response_class=RedirectResponse, tags=["modrinth"])
async def get_jar_for_modrinth(loader: Loader, project_id_or_slug: str, version_id_or_number: str,
                               filename: str) -> RedirectResponse:
    version = await validate_and_get_version_for_loader(loader=loader, project_id_or_slug=project_id_or_slug,
                                                        version_id_or_number=version_id_or_number, filename=filename)

    # Get primary file URL
    primary_file = next((file for file in version.files if file.primary), None)
    if not primary_file:
        raise HTTPException(status_code=404, detail="JAR file not found")

    # Redirect to Modrinth's file URL
    return RedirectResponse(url=primary_file.url)
