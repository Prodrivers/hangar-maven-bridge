from fastapi import HTTPException, APIRouter, Depends
from fastapi_xml import XmlAppResponse
from starlette.requests import Request
from starlette.responses import Response

from app.models.modrinth import Loader
from app.modrinth import fetch_modrinth_project_versions_for_loader
from app.settings import settings


async def cache_control(request: Request, response: Response):
    response.headers.update({"Cache-Control": f"public, max-age={settings.cache.metadata_expiration_seconds}"})


router = APIRouter(dependencies=[Depends(cache_control)])


@router.get("/repository/com/modrinth/{loader}/{project_id_or_slug}/maven-metadata.xml",
            response_class=XmlAppResponse, tags=["modrinth"])
async def get_metadata_for_modrinth(loader: Loader, project_id_or_slug: str) -> Response:
    versions = await fetch_modrinth_project_versions_for_loader(project_id_or_slug=project_id_or_slug, loader=loader)
    if not versions:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate the number of versions
    if len(versions) == 0:
        raise HTTPException(status_code=404, detail="No versions found")

    # Get latest version
    latest_version = versions[0]
    # Use latest version's publishing date as Maven's lastUpdated (in YYYYMMDDHHMMSS format)
    last_updated_maven_format = latest_version.date_published.strftime("%Y%m%d%H%M%S")

    metadata = f"""<metadata>
  <groupId>com.modrinth.{loader}</groupId>
  <artifactId>{project_id_or_slug}</artifactId>
  <versioning>
    <latest>{latest_version.version_number}</latest>
    <release>{latest_version.version_number}</release>
    <versions>
"""
    for version in versions:
        metadata += f"      <version>{version.version_number}</version>\n"

    metadata += f"""    </versions>
    <lastUpdated>{last_updated_maven_format}</lastUpdated>
  </versioning>
</metadata>
"""
    return Response(content=metadata.strip(), media_type="application/xml")
