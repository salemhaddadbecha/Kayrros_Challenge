from fastapi import FastAPI
from app.routers import hotspots, docs

app = FastAPI(
    title="Kayrros models API",
    description="API for querying fire hotspots and clusters",
    version="1.0.0",
)

app.include_router(hotspots.router)
app.include_router(docs.router, prefix="")  # include docs router at root

