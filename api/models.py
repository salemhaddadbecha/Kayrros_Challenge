from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, UniqueConstraint, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
from geoalchemy2 import Geometry

# Base class for all ORM models
Base = declarative_base()


# Enum for cluster status
class ClusterStatusEnum(str, PyEnum):
    """
    Enum representing the possible statuses of a fire cluster.
    """
    DETECTED = "DETECTED"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


# Cluster ORM Model
class Cluster(Base):
    """
    ORM model representing a cluster of hotspots.
    """
    __tablename__ = "cluster"
    __table_args__ = {"schema": "live"}  # Use the 'live' schema in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(ClusterStatusEnum), nullable=False, default=ClusterStatusEnum.DETECTED)
    # Status of the cluster, constrained to ClusterStatusEnum, defaults to DETECTED
    hotspots = relationship("Hotspot", back_populates="cluster")
    # One-to-many relationship with Hotspot; cluster.hotspots returns list of Hotspot objects


# Hotspot ORM Model
class Hotspot(Base):
    """
        ORM model representing an individual fire hotspot.
    """
    __tablename__ = "hotspot"
    __table_args__ = (
        UniqueConstraint("sensing_time", "geometry", "source", name="uix_hotspot_unique"),
        # Ensure no duplicate hotspot entries for same time, location, and source
        {"schema": "live"}
    )

    id = Column(Integer, primary_key=True, index=True)
    sensing_time = Column(TIMESTAMP(timezone=True), nullable=False)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    source = Column(String, nullable=False)
    cluster_id = Column(Integer, ForeignKey("live.cluster.id", onupdate="CASCADE", ondelete="RESTRICT"))
    # Foreign key referencing the cluster this hotspot belongs to
    # Updates cascade, deletion restricted to preserve historical data
    cluster = relationship("Cluster", back_populates="hotspots")
    # Many-to-one relationship back to Cluster; hotspot.cluster returns parent Cluster
