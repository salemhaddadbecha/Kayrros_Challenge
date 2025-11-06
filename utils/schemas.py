"""
Pydantic schemas for Hotspot and Cluster data validation and serialization.
Used in FastAPI API endpoints for request validation and response formatting.
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# Base schema for Hotspot
class HotspotBase(BaseModel):
    """
    Base schema representing common fields of a Hotspot.
    Used as a parent for creation and read schemas.
    """
    sensing_time: datetime
    source: str


class HotspotCreate(HotspotBase):
    """
        Schema for creating a new Hotspot entry.
        Inherits from HotspotBase, no additional fields required.
    """
    pass


class HotspotRead(HotspotBase):
    """
        Schema for returning Hotspot data in API responses.
    """
    id: int
    cluster_id: Optional[int]
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        orm_mode = True


class ClusterRead(BaseModel):
    """
    Schema for returning Cluster data in API responses.
    Includes list of associated hotspots.
    """
    id: int
    status: str
    hotspots: list[HotspotRead] = []

    class Config:
        """
           Pydantic configuration for ORM mode.
           Enables reading data directly from SQLAlchemy ORM objects.
        """
        orm_mode = True
