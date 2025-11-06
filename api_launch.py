from fastapi import FastAPI
from api.routers import hotspots

app = FastAPI(
    title="Kayrros Hotspot API",
    description="API for querying fire hotspots and clusters",
    version="1.0.0",
)

app.include_router(hotspots.router)
