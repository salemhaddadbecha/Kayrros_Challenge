import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from datetime import datetime
import os
from api.models import Hotspot
import logging

# Create logs directory if it does not exist
os.makedirs("logs", exist_ok=True)
# Build dynamic log file name with timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = f"logs/ingestion_{timestamp}.log"
# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# Database connection Setup
DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'postgres')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME', 'kayrros_hotspots')}"
# Create SQLAlchemy engine for connecting to PostgreSQL
engine = create_engine(DB_URL)
# Create session factory
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()  # Instantiate a session for database operations

# Data Sources
DAILY_URLS = {
    "EU": {
        "FIRMS_MODIS": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Europe_24h.csv",
        "FIRMS_SUOMI_VIIRS": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Europe_24h.csv",
    }
}


def parse_datetime(acq_date, acq_time):
    """
    Convert acquisition date and time into a Python datetime object.

    Parameters:
        acq_date (str): Date in 'YYYY-MM-DD' format
        acq_time (int): Time in HHMM format (e.g., 730 for 07:30)

    Returns:
        datetime: Combined datetime object
    """
    acq_time_str = f"{acq_time:04d}"  # Pad time to 4 digits, e.g., 730 -> "0730"
    hour = int(acq_time_str[:2])  # Extract hour
    minute = int(acq_time_str[2:])  # Extract minute
    return datetime.strptime(
        f"{acq_date} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M"
    )  # Combine into datetime


def ingest_firms_csv(url, source):
    """
    Ingest fire hotspots from a NASA FIRMS CSV and insert them into the database.

    Parameters:
        url (str): URL or local path to the CSV file
        source (str): Name of the satellite source (MODIS, VIIRS)
    """
    df = pd.read_csv(url)  # Load CSV data into a pandas DataFrame
    hotspots = []  # List to hold Hotspot objects before insertion
    for _, row in df.iterrows():
        sensing_time = parse_datetime(
            row["acq_date"], row["acq_time"]
        )  # Parse acquisition datetime
        # create a geometric point using the coordinates of the fire hotspot to be able to use ST_Within, ST_Distance, ST_ClusterKMeans after
        # ; otherwise it will be too slow or even impossible
        point = from_shape(
            Point(row["longitude"], row["latitude"]), srid=4326
        )  # Convert to PostGIS POINT
        # Create a Python object corresponding to live.hotspot
        hotspot = Hotspot(
            sensing_time=sensing_time,
            geometry=point,
            source=source,
            cluster_id=None,
        )
        hotspots.append(hotspot)

    # Bulk insert with conflict handling
    inserted_count = 0
    for h in hotspots:
        stmt = (
            pg_insert(Hotspot)
            .values(
                sensing_time=h.sensing_time,
                geometry=h.geometry,
                source=h.source,
                cluster_id=h.cluster_id,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "sensing_time",
                    "geometry",
                    "source",
                ]  # Avoid duplicates on these columns
            )
        )
        result = session.execute(stmt)  # Execute insert statement for each hotspot

        # result.rowcount = 1 if inserted, 0 if skipped
        if result.rowcount == 1:
            inserted_count += 1

    session.commit()  # Commit all inserts to the database
    # Log the ingestion summary
    logging.info(
        f"{source}: Found {len(hotspots)} records — Inserted {inserted_count} (skipped {len(hotspots) - inserted_count})."
    )
    print(f"{source}: Ingested {inserted_count} new hotspots")


def run_ingestion():
    """
    Run the ingestion pipeline for all defined regions and satellite sources.
    """
    for region, sources in DAILY_URLS.items():  # Loop over regions (e.g., EU)
        for source_name, url in sources.items():  # Loop over satellite sources
            ingest_firms_csv(url, source_name)


if __name__ == "__main__":
    run_ingestion()
