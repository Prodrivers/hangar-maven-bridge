from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi_xml import XmlAppResponse
from starlette.requests import Request
from starlette.responses import Response

from app.hangar import platform_type, fetch_version_metadata
from app.settings import settings


async def cache_control(request: Request, response: Response):
    response.headers.update({"Cache-Control": f"public, max-age={settings.cache.pom_expiration_seconds}"})


router = APIRouter(dependencies=[Depends(cache_control)])


@router.get("/repository/io/papermc/hangar/{platform}/{channel}/{slug}/{version}/{filename}.pom",
            response_class=XmlAppResponse, tags=["hangar_with_platform_and_channel"])
async def get_pom_with_platform_and_channel(platform: platform_type, slug: str, channel: Optional[str], version: str,
                                            filename: str) -> Response:
    # Check that the filename matches the pattern "{slug}-{version}.pom"
    expected_filename = f"{slug}-{version}"
    if filename != expected_filename:
        raise HTTPException(status_code=400, detail="Filename does not match expected pattern")

    version_metadata = await fetch_version_metadata(slug, version)

    dependencies = version_metadata.get("dependencies", [])

    # Generate group ID depending on parameters
    maven_group_id = f"io.papermc.hangar.{platform}"
    if channel is not None:
        maven_group_id += f".{channel}"

    pom_content = f"""<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>{maven_group_id}</groupId>
  <artifactId>{slug}</artifactId>
  <version>{version}</version>
  <dependencies>
"""
    for dep in dependencies:
        pom_content += f"""    <dependency>
      <groupId>{dep['namespace']}</groupId>
      <artifactId>{dep['name']}</artifactId>
      <version>{dep['version']}</version>
    </dependency>
"""
    pom_content += """  </dependencies>
</project>
"""
    return Response(content=pom_content.strip(), media_type="application/xml")


@router.get("/repository/io/papermc/hangar/{platform}/{slug}/{version}/{filename}.pom", response_class=XmlAppResponse,
            tags=["hangar_with_platform"])
async def get_pom_with_platform(platform: platform_type, slug: str, version: str, filename: str) -> Response:
    return await get_pom_with_platform_and_channel(platform=platform, channel=None, slug=slug, version=version,
                                                   filename=filename)


@router.head("/repository/io/papermc/hangar/{platform}/{channel}/{slug}/{version}/{filename}.pom",
             tags=["hangar_with_platform_and_channel"])
async def head_pom_with_platform_and_channel(
        platform: platform_type,
        channel: Optional[str],
        slug: str,
        version: str,
        filename: str
) -> Response:
    # Validate the filename pattern for POM files
    expected_filename = f"{slug}-{version}"
    if filename != expected_filename:
        return Response(status_code=400)

    # Fetch version metadata (same as in the GET method)
    version_metadata = await fetch_version_metadata(slug, version)

    if not version_metadata:
        return Response(status_code=404)

    # Prepare headers for the HEAD request
    headers = {
        "Content-Type": "application/xml",
        "Content-Length": str(len(str(version_metadata))),
        # Optional: size of the content (you may calculate it based on actual content)
        "Last-Modified": version_metadata["createdAt"],  # Set to createdAt time of version
    }

    return Response(status_code=200, headers=headers)


@router.head("/repository/io/papermc/hangar/{platform}/{slug}/{version}/{filename}.pom", tags=["hangar_with_platform"])
async def head_pom_with_platform(platform: platform_type, slug: str, version: str, filename: str) -> Response:
    return await head_pom_with_platform_and_channel(platform=platform, channel=None, slug=slug, version=version,
                                                    filename=filename)
