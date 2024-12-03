import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache

from app.routers import api_router, tags_metadata
from app.settings import settings

title = "minecraft-maven-bridge"
version = "1.0.0"
description = "A bridge application that exposes PaperMC's Hangar as a Maven repository."
contact = {
    "name": "Prodrivers",
    "url": "https://prodrivers.fr/"
}
license_info = {
    "name": "The MIT License (MIT)",
    "identifier": "MIT",
}

logger = logging.getLogger(__name__)

# Lifespan handler to initialize FastAPICache
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.cache.backend == 'redis':
        logger.info("Using Redis as cache backend.")

        import redis.asyncio as redis
        from redis.asyncio.connection import ConnectionPool
        from fastapi_cache.backends.redis import RedisBackend

        pool = ConnectionPool.from_url(url=settings.cache.redis_url)
        redis = redis.Redis(connection_pool=pool)
        backend = RedisBackend(redis)
    else:
        logger.info("Using in-memory cache backend.")

        from fastapi_cache.backends.inmemory import InMemoryBackend

        backend = InMemoryBackend()
    FastAPICache.init(backend=backend, prefix=settings.cache.prefix)

    # Control passes here during the app lifespan
    yield

# Initialize app with lifespan
app = FastAPI(
    title=title,
    version=version,
    description=description,
    contact=contact,
    license_info=license_info,
    debug=settings.debug,
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": f"Hello from {title} v{version} by {contact['name']}!"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
