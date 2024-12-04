from typing import Optional

from fastapi import HTTPException, APIRouter, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from app.hangar import platform_type, get_version_download_url
from app.settings import settings


async def cache_control(request: Request, response: Response):
    response.headers.update({"Cache-Control": f"public, max-age={settings.cache.jar_expiration_seconds}"})


router = APIRouter(dependencies=[Depends(cache_control)])


@router.get("/repository/io/papermc/hangar/{platform}/{slug}/{version}/{filename}.jar",
            response_class=RedirectResponse, tags=["hangar_with_platform"])
async def get_jar_with_platform(platform: platform_type, slug: str, version: str, filename: str) -> RedirectResponse:
    return await get_jar_with_platform_and_channel(platform=platform, channel=None, slug=slug, version=version,
                                                   filename=filename)


@router.get("/repository/io/papermc/hangar/{platform}/{channel}/{slug}/{version}/{filename}.jar",
            response_class=RedirectResponse, tags=["hangar_with_platform_and_channel"])
async def get_jar_with_platform_and_channel(platform: platform_type, channel: Optional[str], slug: str, version: str,
                                            filename: str) -> RedirectResponse:
    # Validate that the filename matches the expected "{slug}-{version}.jar" pattern
    expected_filename = f"{slug}-{version}"
    if filename != expected_filename:
        raise HTTPException(status_code=400, detail="Filename does not match expected pattern")

    # Get the download link for the artifact
    download_url = get_version_download_url(slug=slug, platform=platform, version=version)

    # Redirect directly to the Hangar download URL
    return RedirectResponse(url=download_url)
