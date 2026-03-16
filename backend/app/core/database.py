from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# For local development, we default to a local path or fallback SQLite if PG is unavailable
# In production, this should come from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./leadgen.db" # Defaulting to SQLite for immediate local testing without requiring a postgres server immediately
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
