from typing import cast

from fastapi import HTTPException, APIRouter
from fastapi_xml import XmlAppResponse
from starlette.responses import Response

from app.models.modrinth import Loader, ExpandedDependency
from app.modrinth import fetch_modrinth_project_version

router = APIRouter()


async def validate_and_get_version_for_loader(loader: Loader, project_id_or_slug: str, version_id_or_number: str,
                                              filename: str):
    expected_filename = f"{project_id_or_slug}-{version_id_or_number}"
    if filename != expected_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    version = await fetch_modrinth_project_version(project_id_or_slug=project_id_or_slug,
                                                   version_id_or_number=version_id_or_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if loader not in version.loaders:
        raise HTTPException(status_code=404, detail=f"Version does not contain a file for loader {loader}")

    return version


@router.get("/repository/com/modrinth/{loader}/{project_id_or_slug}/{version_id_or_number}/{filename}.pom",
            response_class=XmlAppResponse, tags=["modrinth"])
async def get_pom_for_modrinth(loader: Loader, project_id_or_slug: str, version_id_or_number: str,
                               filename: str) -> Response:
    version = await validate_and_get_version_for_loader(loader=loader, project_id_or_slug=project_id_or_slug,
                                                        version_id_or_number=version_id_or_number, filename=filename)

    pom_content = f"""<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.modrinth.{loader}</groupId>
  <artifactId>{project_id_or_slug}</artifactId>
  <version>{version.version_number}</version>
  <dependencies>
"""
    for dependency in version.dependencies:
        if not isinstance(dependency, ExpandedDependency):
            continue
        expanded_dependency = cast(ExpandedDependency, dependency)
        pom_content += f"""    <dependency>
      <groupId>com.modrinth.{loader}</groupId>
      <artifactId>{expanded_dependency.project_id}</artifactId>
      <version>{expanded_dependency.version_number}</version>
    </dependency>
"""
    pom_content += """  </dependencies>
</project>
"""
    return Response(content=pom_content.strip(), media_type="application/xml")


@router.head("/repository/com/modrinth/{loader}/{project_id_or_slug}/{version_id_or_number}/{filename}.pom",
             tags=["modrinth"])
async def head_pom_for_modrinth(loader: Loader, project_id_or_slug: str, version_id_or_number: str,
                                filename: str) -> Response:
    version = await validate_and_get_version_for_loader(loader=loader, project_id_or_slug=project_id_or_slug,
                                                        version_id_or_number=version_id_or_number, filename=filename)

    # Prepare headers
    headers = {
        "Content-Type": "application/xml",
        "Content-Length": "0",
        "Last-Modified": version.date_published.isoformat(),
    }
    return Response(status_code=200, headers=headers)
