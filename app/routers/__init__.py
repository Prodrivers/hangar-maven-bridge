from fastapi import APIRouter

from .metadata import router as metadata_router
from .pom import router as pom_router
from .jar import router as jar_router

api_router = APIRouter()

api_router.include_router(metadata_router)
api_router.include_router(pom_router)
api_router.include_router(jar_router)

tags_metadata = [
    {
        "name": "default",
        "description": "Uncategorized operations.",
    },
    {
        "name": "with_platform_and_channel",
        "description": "Maven Repository URL implementation that uses both platform and version channel in group ID.",
    },
    {
        "name": "with_platform",
        "description": "Maven Repository URL implementation that uses platform in group ID.",
    }
]
