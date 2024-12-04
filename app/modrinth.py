import asyncio
from typing import Optional, List

import httpx
from aiocache import cached

from app.models.modrinth import Version, Dependency, ExpandedDependency, Project
from app.settings import settings


@cached(ttl=settings.modrinth.cache_project_expiration_seconds)
async def fetch_modrinth_project(project_id_or_slug: str) -> Optional[Project]:
    """
    Fetch Modrinth project's metadata.

    Parameters:
    - project_id_or_slug (str): The ID or slug of the Modrinth project to be fetched.

    Returns:
    - Optional[Project]: A Project object containing the project's metadata if successful, or None if the project could
      not be retrieved.
    """

    url = f"{settings.modrinth.api_base_url}/project/{project_id_or_slug}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return Project(**response.json())
    return None


@cached(ttl=settings.modrinth.cache_version_expiration_seconds)
async def fetch_modrinth_project_versions_for_loader(project_id_or_slug: str, loader: str) -> List[Version]:
    """
    Fetch Modrinth project's versions metadata for a specific loader.

    Parameters:
    - project_id_or_slug (str): The ID or slug of the Modrinth project for which versions are to be fetched.
    - loader (str): The specific loader for which the project's versions are to be retrieved.

    Returns:
    - list[Version]: A list of Version objects containing the project's version metadata for the specified loader.
      Returns an empty list if no versions are found for the loader or if the request fails.
    """

    url = f"{settings.modrinth.api_base_url}/project/{project_id_or_slug}/version"
    params = {
        "loaders": [loader]
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            return [Version(**json_item) for json_item in response.json()]
    return []


@cached(ttl=settings.modrinth.cache_version_expiration_seconds)
async def fetch_modrinth_version_dependency(dependency: Dependency, depth: int) -> ExpandedDependency | Dependency:
    """
    Expand a Modrinth version dependency to include full metadata.

    This function attempts to expand a given dependency by fetching additional version information from Modrinth.
    If the version information is successfully retrieved, an expanded dependency object, containing both the original
    dependency's data and the version data, is returned.

    Parameters:
    - dependency (Dependency): The dependency object to be expanded. It must contain a project ID and optionally a
      version ID.
    - depth (int): The recursion depth for expanding dependencies. If the depth is 0 or less, no expansion occurs.

    Returns:
    - ExpandedDependency | Dependency: An ExpandedDependency object if the version information is successfully retrieved
      and merged with the original dependency. Otherwise, returns the original Dependency object if expansion is not
      possible.
    """

    # If no version is provided, just return the dependency. We do not have enough information to select the proper
    # loader and channel
    if not dependency.version_id:
        return dependency
    # Fetch version from Modrinth
    version = await fetch_modrinth_project_version(dependency.project_id, dependency.version_id,
                                                   expand_dependencies_depth=depth)
    # If we cannot get the version, just return the dependency. Type can be used to differentiate between expanded and
    # non-expanded dependencies
    if not version:
        return dependency
    # Merge retrieved version information with dependency
    return ExpandedDependency(**dependency.__dict__, **version.__dict__)


async def fetch_modrinth_version_dependencies(dependencies: list[Dependency], depth: int) -> List[
    ExpandedDependency | Dependency]:
    """
    Expand Modrinth version dependencies to include full metadata.

    This function takes a list of dependencies and attempts to expand each one to include full version metadata by
    fetching additional information from Modrinth.

    Parameters:
    - dependencies (list[Dependency]): A list of Dependency objects to be expanded.
    - depth (int): The recursion depth for expanding dependencies. If the depth is 0 or less, no expansion occurs.

    Returns:
    - list[ExpandedDependency | Dependency]: A list of dependencies, where each dependency is either expanded to include
      full version metadata or left as is if expansion is not possible.
    """

    # Stop if we go over recurse depth
    if depth <= 0:
        return []
    depth -= 1
    # Fetch all expanded dependencies asynchronously
    return await asyncio.gather(
        *[fetch_modrinth_version_dependency(dependency=dependency, depth=depth) for dependency in dependencies])


@cached(ttl=settings.modrinth.cache_version_expiration_seconds)
async def fetch_modrinth_project_version(project_id_or_slug: str, version_id_or_number: str,
                                         expand_dependencies_depth: int = 1) -> Optional[Version]:
    """
    Fetch Modrinth project's version metadata.

    This function retrieves metadata for a specific version of a Modrinth project.
    If possible, it also expands the dependencies to full version metadata as Modrinth only returns version ID and
    project ID for dependencies.

    Parameters:
    - project_id_or_slug (str): The ID or slug of the Modrinth project.
    - version_id_or_number (str): The ID or version number of the project version to fetch.
    - expand_dependencies_depth (int, optional): The depth to which dependencies should be expanded. Defaults to 1, as
      Maven only has one depth of dependency, there is no need to go further as when exploring the dependencies.

    Returns:
    - Optional[Version]: A Version object containing the project's version metadata if successful, or None if the
      version could not be retrieved.
    """

    url = f"{settings.modrinth.api_base_url}/project/{project_id_or_slug}/version/{version_id_or_number}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            if expand_dependencies_depth <= 0:
                return Version(**data)
            dependencies = [Dependency(**dependency) for dependency in data['dependencies']]
            expanded_dependencies = await fetch_modrinth_version_dependencies(dependencies=dependencies,
                                                                              depth=expand_dependencies_depth)
            data['dependencies'] = expanded_dependencies
            return Version(**data)
    return None
