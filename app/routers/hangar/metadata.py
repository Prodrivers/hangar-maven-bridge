from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi_xml import XmlAppResponse
from starlette.requests import Request
from starlette.responses import Response

from app.hangar import platform_type, fetch_versions_metadata
from app.settings import settings


async def cache_control(request: Request, response: Response):
    response.headers.update({"Cache-Control": f"public, max-age={settings.cache.metadata_expiration_seconds}"})


router = APIRouter(dependencies=[Depends(cache_control)])


@router.get("/repository/io/papermc/hangar/{platform}/{channel}/{slug}/maven-metadata.xml",
            response_class=XmlAppResponse, tags=["hangar_with_platform_and_channel"])
async def get_maven_metadata_with_platform_and_channel(platform: platform_type, slug: str,
                                                       channel: Optional[str]) -> Response:
    versions = await fetch_versions_metadata(slug=slug, platform=platform, channel=channel)

    # Validate the number of versions
    if len(versions) == 0:
        raise HTTPException(status_code=404, detail="No versions found")

    # Latest version and lastUpdated timestamp from the createdAt field
    latest_version = versions[0]
    last_updated = latest_version.get("createdAt", "")

    # Convert to Maven's lastUpdated format (YYYYMMDDHHMMSS)
    last_updated_dt = datetime.fromisoformat(last_updated.rstrip("Z"))
    last_updated_maven_format = last_updated_dt.strftime("%Y%m%d%H%M%S")

    # Generate group ID depending on parameters
    maven_group_id = "io.papermc.hangar"
    if platform is not None:
        maven_group_id += f".{platform}"
    if channel is not None:
        maven_group_id += f".{channel}"

    metadata = f"""<metadata>
  <groupId>{maven_group_id}</groupId>
  <artifactId>{slug}</artifactId>
  <versioning>
    <latest>{latest_version['name']}</latest>
    <release>{latest_version['name']}</release>
    <versions>
"""
    for version in versions:
        metadata += f"      <version>{version['name']}</version>\n"

    metadata += f"""    </versions>
    <lastUpdated>{last_updated_maven_format}</lastUpdated>
  </versioning>
</metadata>
"""
    return Response(content=metadata.strip(), media_type="application/xml")


@router.get("/repository/io/papermc/hangar/{platform}/{slug}/maven-metadata.xml", response_class=XmlAppResponse,
            tags=["hangar_with_platform"])
async def get_maven_metadata_with_platform(platform: platform_type, slug: str) -> Response:
    return await get_maven_metadata_with_platform_and_channel(platform=platform, channel=None, slug=slug)
