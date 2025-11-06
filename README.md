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
```
This fetches the latest fire hotspots from NASA FIRMS and inserts them into the database.
cluster_id is currently null as clustering is not implemented yet.

### 3. Connect to database: 
```bash
psql -h localhost -p 5433 -U postgres -d kayrros_hotspots
select * from live.hotspot;
```
### Running Tests
1. Install pytest:
```bash
pip install pytest
pytest tests/
```
Planned / Next steps:
- CSV ingestion tests: Verify ingest_firms_csv() correctly inserts hotspots into PostgreSQL without duplicates.
- API endpoint tests: Ensure FastAPI endpoints return correct hotspots and cluster data.
- Edge case handling: Test ingestion with missing or invalid data.
- Integration tests: Run end-to-end flow: CSV → ingestion → database → API query.


### API Endpoints
#### /hotspots/recent
- Returns hotspots from the last 24h
- Optional query parameters:
    - bbox → Bounding box "min_lon,min_lat,max_lon,max_lat"
    - source → Filter by satellite source

Each hotspot includes id, sensing_time, source, cluster_id, latitude, and longitude.

#### /hotspots/clustered
- Returns all clusters with their associated hotspots.
- Currently, clusters exist but cluster_id in hotspots is null.

####  Clustering (Not Implemented)
- Spatial proximity: group hotspots within X km
- Temporal proximity: group hotspots detected within Y hours
- Possible implementation:
  - PostGIS ST_ClusterDBSCAN
  - Custom SQL queries

### Next Steps / Improvements

- Implement clustering logic to populate `cluster_id`
- Add error handling for ingestion failures
- Implement unit and integration tests for API endpoints
- Add caching or pagination for large result sets

### LLM Usage
- Used AI (ChatGPT) to help organize the README, suggest file structure, and improve clarity.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostGIS Documentation](https://postgis.net/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

 
