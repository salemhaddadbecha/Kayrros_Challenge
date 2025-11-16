# Data Engineer Python API Test - Fire Hotspots

Welcome to Kayrros technical test!

## Context

This system provides real-time fire detection data to help firefighters and emergency response teams:
- **Locate active fires** from satellite observations
- **Track fire intensity** using Fire Radiative Power (FRP) measurements
- **Monitor fire evolution** across different satellite sources
- **Query historical patterns** for risk assessment and resource allocation

## Project Objectives

Build a **small, production-ready system** that:

1. **Creates a database schema** for storing fire hotspots and clusters using PostgreSQL with PostGIS. A base schema is provided in `db/schema/live.sql`. The schema is mounted into the Postgres container and initialized (see `docker-compose.yml`).
2. **Implements an ingestion pipeline** to fetch and process fire hotspot data from NASA FIRMS (Fire Information for Resource Management System).
3. **Exposes REST API endpoints** to query hotspots and clusters.  
4. **Bonus**: Design considerations for clustering hotspots spatially and temporally.  

## Project Structure

```
.
├── api/
│   ├── ingest.py           # ETL / ingestion logic
│   ├── models.py           # SQLAlchemy models
│   └── routers/
│       └── hotspots.py     # API endpoints
├── app/
│   └── routers/
│       └── docs.py 
├── db/
│   └── schema/
│       └── live.sql        # Database schema (hotspot & cluster tables)
├── utils/
│   └── schemas.py          # Pydantic schemas for validation
├── logs                   # Logs folder containing logs for each execution
├── db.py                   # DB session and engine
├── api_launch.py                  # FastAPI app entrypoint
├── static/input/           # Sample CSVs
├── tests/                  # Test files
├── docker-compose.yml      # Docker stack definition
├── Dockerfile              # API container image
├── Makefile                # Development utilities
└── pyproject.toml          # Python dependencies

```


**Data Sources**:
   
Ingest data from two NASA satellite-based fire detection systems, both updated **daily** with the last 24 hours of observations:
   
```python
DAILY_URLS = {
       "EU": {
           "FIRMS_MODIS": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Europe_24h.csv",
           "FIRMS_SUOMI_VIIRS": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Europe_24h.csv"
       }
   }
```

**Data Schemas**:

**MODIS**:

   - `latitude`, `longitude`: Geographic coordinates (decimal degrees)
   - `brightness`: Brightness temperature (Kelvin) at 4 µm
   - `scan`, `track`: Pixel size (km) in scan and track directions
   - `acq_date`, `acq_time`: Acquisition date (YYYY-MM-DD) and time (HHMM UTC)
   - `satellite`: A=Aqua, T=Terra
   - `confidence`: Detection confidence (0-100)
   - `version`: Product version
   - `bright_t31`: Brightness temperature at 11 µm (Kelvin)
   - `frp`: Fire Radiative Power (MW) - key metric for fire intensity
   - `daynight`: D=day, N=night

   **VIIRS**:

   - `latitude`, `longitude`: Geographic coordinates (decimal degrees)
   - `bright_ti4`: Brightness temperature at 4 µm (Kelvin)
   - `scan`, `track`: Pixel size (km) in scan and track directions
   - `acq_date`, `acq_time`: Acquisition date (YYYY-MM-DD) and time (HHMM UTC)
   - `satellite`: N=Suomi-NPP, J1=NOAA-20
   - `confidence`: nominal, low, or high
   - `version`: Product version
   - `bright_ti5`: Brightness temperature at 11 µm (Kelvin)
   - `frp`: Fire Radiative Power (MW) - key metric for fire intensity
   - `daynight`: D=day, N=night
   
   **Note**: These URLs are publicly accessible and require no authentication. The data is refreshed daily (hint: make sure to handle incremental updates to avoid duplicate entries!)


## Running the project
### 1. Start Docker Stack

```bash
make docker-up
#Or:
docker-compose up -d
```

This will start:
- PostgreSQL with PostGIS (port 5432)
- FastAPI application (port 8000)

Access the API at: http://localhost:8000/docs

### View Logs

```bash
make docker-logs
make docker-logs-api
make docker-logs-db
#Or: 
docker-compose logs -f api
docker-compose logs -f postgres
```

### 2. Run Ingestion Script
```bash
docker-compose exec api python api/ingest.py
#Or: docker-compose exec api python -m api.ingest
```
This fetches the latest fire hotspots from NASA FIRMS and inserts them into the database.
cluster_id is currently null as clustering is not implemented yet.

#### Logs
Ingestion logs are automatically generated in the logs/ directory.
- Each run creates a file named: logs/ingestion_<timestamp>.log
- Logs include:
  - Timestamped execution details
  - Source-by-source ingestion progress
  - Number of discovered vs. inserted records 
  - Skipped records due to duplication handling
This ensures full traceability of the ingestion process for debugging, monitoring, and validation.

### 3. Connect to database: 
```bash
psql -h localhost -p 5433 -U postgres -d kayrros_hotspots
select * from live.hotspot;
# SELECT ST_AsText(geometry) FROM live.hotspot; #Back geo to its orignal format
```

### Running Tests
1. Install pytest:
```bash
pip install pytest
pytest tests/
```

### API Endpoints
#### /hotspots/recent
- Returns hotspots from the last 24h
- Optional query parameters:
    - source → Filter by satellite source

Each hotspot includes id, sensing_time, source, cluster_id, latitude, and longitude.

#### /hotspots/clustered
- Returns all clusters with their associated hotspots.
- Currently, clusters exist but cluster_id in hotspots is null.


#### Continuous Integration (CI)
This project uses GitHub Actions for continuous integration, running automatically on push and pull request events.

The CI pipeline performs:

- Python environment setup (Python 3.9)
- Dependency installation
- Unit tests execution with pytest
- Code linting using flake8
- Code formatting checks with black

The workflow is defined in .github/workflows/python-tests.yml.

####  Clustering (Not Implemented)
- Spatial proximity: group hotspots within X km(Hotspots that are geographically close).
- Temporal proximity: group hotspots detected within Y hours(Hotspots that occur around the same time).
- Possible implementation:
  - PostGIS ST_ClusterDBSCAN: directly cluster points in the database based on distance and optional time filtering.
    - Custom SQL queries or Python Logic: 
      - Fetch hotspots from the last 24–48 hours.
      - Compute distances between points (Haversine or PostGIS geometry functions).
      - Group points that are within distance X and time window Y into a cluster.
      - Insert a row in the cluster table for each group.
      - Update hotspot.cluster_id for each hotspot in that cluster.

### Next Steps / Improvements

- Implement clustering logic to populate `cluster_id`
- Implement unit and integration tests for API endpoints
- Add caching or pagination for large result sets

### LLM Usage
AI assistance (ChatGPT) was used throughout the project to accelerate development and improve documentation quality.
- README drafting and refinement:
- Debugging guidance: assisted in diagnosing issues related to Docker, environment variables, SQLAlchemy sessions, and ingestion logic.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostGIS Documentation](https://postgis.net/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

 
