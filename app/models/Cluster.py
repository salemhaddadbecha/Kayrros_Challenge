from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

# Base class for all ORM models
from db import Base


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
    ORM model representing a group of hotspots.
    """

    __tablename__ = "cluster"
    __table_args__ = {"schema": "live"}  # Use the 'live' schema in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    status = Column(
        SQLEnum(ClusterStatusEnum), nullable=False, default=ClusterStatusEnum.DETECTED
    )
    # Status of the cluster, constrained to ClusterStatusEnum, defaults to DETECTED
    hotspots = relationship("Hotspot", back_populates="cluster")
    # One-to-many relationship with models; cluster.hotspots returns list of models objects
