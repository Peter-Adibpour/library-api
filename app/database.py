from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = None
SessionLocal = None

if settings.storage_backend == "database":
    engine = create_engine(settings.database_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()