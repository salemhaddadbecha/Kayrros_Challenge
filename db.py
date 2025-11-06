from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER','postgres')}:{os.getenv('DB_PASSWORD','postgres')}@{os.getenv('DB_HOST','postgres')}:{os.getenv('DB_PORT',5432)}/{os.getenv('DB_NAME','kayrros_hotspots')}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
