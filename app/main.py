import logging

from fastapi import FastAPI

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

# Initialize app with lifespan
app = FastAPI(
    title=title,
    version=version,
    description=description,
    contact=contact,
    license_info=license_info,
    debug=settings.debug,
    openapi_tags=tags_metadata
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": f"Hello from {title} v{version} by {contact['name']}!", "title": title, "version": version,
            "description": description, "contact": contact, "license_info": license_info}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
