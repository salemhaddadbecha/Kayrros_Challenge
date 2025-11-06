from api.ingest import parse_datetime


# import pytest
# from api.ingest import ingest_firms_csv
# from sqlalchemy import create_engine, text
#
# # Use a temporary database for testing
# TEST_DB_URL = "postgresql://postgres:postgres@postgres:5432/kayrros_hotspots"
#
#
# @pytest.fixture
# def db_engine():
#     engine = create_engine(TEST_DB_URL)
#     yield engine
#     # cleanup after test
#     with engine.connect() as conn:
#         conn.execute(text("DELETE FROM live.hotspot"))
#         conn.commit()
#
#
# def test_ingest_csv(db_engine):
#     # sample CSV data (could also use a small file from static/input)
#     sample_csv = "tests/sample_firms.csv"
#
#     # Call your ingestion function
#     ingest_firms_csv(sample_csv, source="FIRMS_MODIS", engine=db_engine)
#
#     # Assert data was inserted
#     with db_engine.connect() as conn:
#         result = conn.execute(text("SELECT COUNT(*) FROM live.hotspot"))
#         count = result.scalar()
#         assert count > 0


def test_parse_datetime():
    dt = parse_datetime("2025-11-06", 730)
    assert dt.hour == 7
    assert dt.minute == 30
