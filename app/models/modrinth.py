from datetime import datetime

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal

DependencyType = Literal["required", "optional", "incompatible", "embedded"]
FileType = Literal["required-resource-pack", "optional-resource-pack"]
Loader = Literal["paper", "velocity", "waterfall", "bungeecord", "minecraft", "fabric", "forge", "sponge", "folia"]
RequestedStatus = Literal["listed", "archived", "draft", "unlisted"]
Status = Literal["listed", "archived", "draft", "unlisted", "scheduled", "unknown"]
VersionType = Literal["release", "beta", "alpha", "unlisted", "scheduled", "unknown"]

class FileHashes(BaseModel):
    sha512: str
    sha1: str

class File(BaseModel):
    hashes: FileHashes
    url: HttpUrl
    filename: str
    primary: bool
    size: int
    file_type: Optional[FileType]

class Dependency(BaseModel):
    version_id: Optional[str]
    project_id: Optional[str]
    file_name: Optional[str]
    dependency_type: DependencyType

class Version(BaseModel):
    name: str
    version_number: str
    changelog: Optional[str]
    dependencies: List[Dependency]
    game_versions: List[str]
    version_type: VersionType
    loaders: List[Loader]
    featured: bool
    status: Status
    requested_status: Optional[RequestedStatus]
    id: str
    project_id: str
    author_id: str
    date_published: datetime
    downloads: int
    changelog_url: Optional[str]
    files: List[File]

class ExpandedDependency(Dependency, Version):
    pass

from pydantic import BaseModel
from typing import Optional

class License(BaseModel):
    id: str
    name: str
    url: Optional[str]

from datetime import datetime

class GalleryImage(BaseModel):
    url: str
    featured: bool
    title: Optional[str]
    description: Optional[str]
    created: datetime
    ordering: int

class ModeratorMessage(BaseModel):
    message: str
    body: Optional[str]

class Project(BaseModel):
    id: str
    team: str
    body_url: Optional[str]
    moderator_message: Optional[ModeratorMessage]
    published: datetime
    updated: datetime
    approved: Optional[datetime]
    queued: Optional[datetime]
    followers: int
    license: License
    versions: List[str]
    game_versions: List[str]
    loaders: List[Loader]
    gallery: List[GalleryImage]
