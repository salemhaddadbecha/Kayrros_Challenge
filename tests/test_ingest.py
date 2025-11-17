from ingestion.ingest import parse_datetime
from api.models import Hotspot
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from datetime import datetime, timezone


def test_parse_datetime():
    dt = parse_datetime("2025-11-06", 730)
    assert dt.hour == 7
    assert dt.minute == 30


def test_geometry_conversion():
    point = Point(10.0, 20.0)
    geo = from_shape(point, srid=4326)
    assert geo is not None
    # Check that geo has correct SRID attribute (optional)
    assert hasattr(geo, "desc")  # geoalchemy2 returns a WKBElement with .desc


def test_hotspot_object_creation():
    sensing_time = datetime.now(timezone.utc)
    point = from_shape(Point(10, 20), srid=4326)
    h = Hotspot(
        sensing_time=sensing_time, geometry=point, source="MODIS", cluster_id=None
    )
    assert h.sensing_time == sensing_time
    assert h.source == "MODIS"
    assert h.cluster_id is None
    assert h.geometry is not None
