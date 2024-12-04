from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Cache(BaseModel):
    pom_expiration_seconds: int = 3600
    metadata_expiration_seconds: int = 3600
    jar_expiration_seconds: int = 3600


class Hangar(BaseModel):
    api_base_url: str = 'https://hangar.papermc.io/api/v1'
    cache_project_expiration_seconds: int = 3600
    cache_project_max_size: int = 20
    cache_version_expiration_seconds: int = 3600
    cache_version_max_size: int = 20
    versions_limit_per_batch: int = 20
    versions_total_to_fetch: int = 20


class Modrinth(BaseModel):
    api_base_url: str = 'https://api.modrinth.com/v2'
    cache_project_expiration_seconds: int = 3600
    cache_project_max_size: int = 20
    cache_version_expiration_seconds: int = 3600
    cache_version_max_size: int = 20


class Settings(BaseSettings):
    debug: bool = False
    cache: Cache = Cache()
    hangar: Hangar = Hangar()
    modrinth: Modrinth = Modrinth()

    model_config = SettingsConfigDict(env_prefix='MC_MAVEN_BRIDGE__', env_file='.env', env_nested_delimiter='__')


settings = Settings()
