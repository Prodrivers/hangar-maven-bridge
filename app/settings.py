from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Cache(BaseModel):
    backend: str = 'inmemory'
    redis_url: str = ''
    prefix: str = 'hangar_maven_bridge_'
    pom_expiration: int = 3600
    metadata_expiration: int = 3600

class Hangar(BaseModel):
    api_base_url: str = 'https://hangar.papermc.io/api/v1'
    cache_project_expiration: int = 3600
    cache_version_expiration: int = 3600
    versions_limit_per_batch: int = 20
    versions_total_to_fetch: int = 20

class Settings(BaseSettings):
    debug: bool = False
    cache: Cache = Cache()
    hangar: Hangar = Hangar()

    model_config = SettingsConfigDict(env_prefix='BRIDGE_', env_file='.env', env_nested_delimiter='__')

settings = Settings()
