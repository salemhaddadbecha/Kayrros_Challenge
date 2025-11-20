from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.Cluster import Cluster

# Base class for all ORM models
from db import Base


# models ORM Model
class Hotspot(Base):
    """
    ORM model representing an individual fire hotspot.
    """

    __tablename__ = "hotspot"
    __table_args__ = (
        UniqueConstraint(
            "sensing_time", "geometry", "source", name="uix_hotspot_unique"
        ),
        # Ensure no duplicate hotspot entries for same time, location, and source
        {"schema": "live"},
    )

    id = Column(Integer, primary_key=True, index=True)
    sensing_time = Column(TIMESTAMP(timezone=True), nullable=False)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    source = Column(String, nullable=False)
    cluster_id = Column(
        Integer, ForeignKey("live.cluster.id", onupdate="CASCADE", ondelete="RESTRICT")
    )
    # Foreign key referencing the cluster this hotspot belongs to
    # Updates cascade, deletion restricted to preserve historical data
    cluster = relationship("Cluster", back_populates="hotspots")
    # Many-to-one relationship back to Cluster; hotspot.cluster returns parent Cluster
