from fastapi import APIRouter

from .hangar import router as hangar_router
from .modrinth import router as modrinth_router

api_router = APIRouter()

api_router.include_router(hangar_router)
api_router.include_router(modrinth_router)

tags_metadata = [
    {
        "name": "default",
        "description": "Uncategorized operations.",
    },
    {
        "name": "hangar_with_platform_and_channel",
        "description": "Maven Repository URL implementation for PaperMC's Hangar that uses both platform and version channel in group ID.",
    },
    {
        "name": "hangar_with_platform",
        "description": "Maven Repository URL implementation for PaperMC's Hangar that uses platform in group ID.",
    },
    {
        "name": "modrinth",
        "description": "Maven Repository URL implementation for Modrinth.",
    }
]
