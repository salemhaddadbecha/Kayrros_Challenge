from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.models import Hotspot, Cluster
from utils.schemas import HotspotRead, ClusterRead
from datetime import datetime, timedelta
from db import get_db
from geoalchemy2.shape import to_shape

# Router Initialization
router = APIRouter()  # Create a FastAPI router instance to register endpoints


@router.get("/hotspots/recent", response_model=list[HotspotRead])
def get_recent_hotspots(
        bbox: str = Query(None, description="Bounding box 'min_lon,min_lat,max_lon,max_lat'"),
        source: str = Query(None),
        db: Session = Depends(get_db)
):
    """
    Retrieve fire hotspots detected in the last 24 hours, optionally filtered by bounding box and source.

    Parameters:
        bbox (str, optional): A string in the format 'min_lon,min_lat,max_lon,max_lat' to filter hotspots spatially.
        source (str, optional): Satellite source to filter hotspots (MODIS, VIIRS).
        db (Session): SQLAlchemy database session injected via FastAPI Depends.

    Returns:
        list[HotspotRead]: A list of hotspots with id, sensing_time, source, cluster_id, latitude, longitude.
    """

    # Start a query on the Hotspot table
    query = db.query(Hotspot)

    # Calculate the datetime 24 hours ago from current UTC time
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    # Apply bounding box filter if provided
    query = query.filter(Hotspot.sensing_time >= twenty_four_hours_ago)

    if bbox:
        # Convert bbox string into float coordinates
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
        # Construct WKT polygon for PostGIS spatial query
        bbox_wkt = f'POLYGON(({min_lon} {min_lat}, {min_lon} {max_lat}, {max_lon} {max_lat}, {max_lon} {min_lat}, {min_lon} {min_lat}))'
        # Filter hotspots within the bounding box using ST_Within
        query = query.filter(text(f"ST_Within(geometry, ST_GeomFromText('{bbox_wkt}', 4326))"))

    # Apply source filter if provided
    if source:
        query = query.filter(Hotspot.source == source)

    # Execute the query and retrieve all matching hotspots
    hotspots = query.all()

    # Convert PostGIS POINT geometry into latitude and longitude
    result = []
    for h in hotspots:
        point = to_shape(h.geometry)  # Convert PostGIS POINT to Shapely Point
        result.append(HotspotRead(
            id=h.id,
            sensing_time=h.sensing_time,
            source=h.source,
            cluster_id=h.cluster_id,
            latitude=point.y,  # Latitude from Shapely Point
            longitude=point.x  # Longitude from Shapely Point
        ))

    # Return the list of HotspotRead objects
    return result


@router.get("/hotspots/clustered", response_model=list[ClusterRead])
def get_clusters(db: Session = Depends(get_db)):
    """
        Retrieve all hotspot clusters from the database.

        Parameters:
            db (Session): SQLAlchemy database session injected via FastAPI Depends.

        Returns:
            list[ClusterRead]: A list of cluster objects with id and status.
        """
    # Query all clusters from the Cluster table
    clusters = db.query(Cluster).all()
    # Return the list of ClusterRead objects
    return clusters
