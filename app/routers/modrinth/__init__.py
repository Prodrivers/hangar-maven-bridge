from fastapi import APIRouter

from .jar import router as jar_router
from .metadata import router as metadata_router
from .pom import router as pom_router

router = APIRouter()

router.include_router(metadata_router)
router.include_router(pom_router)
router.include_router(jar_router)
