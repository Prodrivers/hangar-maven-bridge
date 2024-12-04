from typing import Literal, Optional

import httpx
from fastapi import HTTPException
from fastapi_cache.decorator import cache

from app.settings import settings

platform_type = Literal["paper", "velocity", "waterfall"]


# Fetch project metadata from the Hangar API, with caching
@cache(expire=settings.hangar.cache_project_expiration)
async def fetch_project_metadata(slug: str) -> dict[str, any]:
    url = f"{settings.hangar.api_base_url}/projects/{slug}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found")
        return response.json()


async def fetch_paginated_versions(slug: str, platform: Optional[platform_type] = None, channel: Optional[str] = None,
                                   limit: int = 10, offset: int = 0) -> tuple[dict[str, any], dict[str, any]]:
    """
    Fetch versions of a specific plugin (slug) from the Hangar API with pagination.
    :param slug: The slug of the project.
    :param platform: Filter results to a supported platform.
    :param channel: Filter results to a specific versions channel.
    :param limit: The number of versions to fetch per request.
    :param offset: The starting point for fetching versions.
    :return: A list of versions and the pagination details.
    """

    url = f"{settings.hangar.api_base_url}/projects/{slug}/versions"

    params = {
        "limit": limit,
        "offset": offset,
        "includeHiddenChannels": False
    }
    if platform is not None:
        params["platform"] = platform.upper()
    if channel is not None:
        params["channel"] = channel

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return data['result'], data['pagination']


# Fetch specific version metadata from the Hangar API, with caching
@cache(expire=settings.hangar.cache_version_expiration)
async def fetch_versions_metadata(slug: str, platform: Optional[platform_type] = None, channel: Optional[str] = None) -> \
list[dict[str, any]]:
    """
    Fetch versions of a specific plugin (slug) from the Hangar API with pagination.
    :param slug: The slug of the project.
    :param platform: Filter results to a supported platform.
    :param channel: Filter results to a specific versions channel.
    :return: A list of versions and the pagination details.
    """

    limit = settings.hangar.versions_limit_per_batch
    offset = 0
    all_versions = []

    while True:
        versions, pagination = await fetch_paginated_versions(slug=slug, platform=platform, channel=channel,
                                                              limit=limit, offset=offset)
        all_versions.extend(versions)

        # Check if there are no more pages to fetch or that we will go over the number of versions to fetch
        if offset + limit >= pagination['count'] or len(all_versions) >= settings.hangar.versions_total_to_fetch:
            break

        # Update offset to fetch the next page
        offset += limit

    return all_versions


# Fetch specific version metadata from the Hangar API, with caching
@cache(expire=settings.hangar.cache_version_expiration)
async def fetch_version_metadata(slug: str, version: str) -> dict[str, any]:
    """
    Fetch metadata for a specific version of a plugin from the Hangar API.
    :param slug: The slug of the project.
    :param version: The specific version to fetch metadata for.
    :return: The metadata for the specified version.
    """

    url = f"{settings.hangar.api_base_url}/projects/{slug}/versions/{version}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Version not found")
        return response.json()


def get_version_download_url(slug: str, platform: platform_type, version: str) -> str:
    """
    Returns the download URL for a specific version of a plugin from the Hangar API.
    :param slug: The slug of the project.
    :param platform: The platform to download for.
    :param version: The specific version to fetch metadata for.
    :return: The download URL for the specified version.
    """

    return f"{settings.hangar.api_base_url}/projects/{slug}/versions/{version}/{platform}/download"
