import pytest
from fastapi.testclient import TestClient
from testcontainers.community.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.services.database import DatabaseMemberService, DatabaseBookService
from app.config import settings

@pytest.fixture(scope="session")
def postgres_container():
    """Spin up a disposable PostgreSQL container for the entire test session."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="function")
def db_session_factory(postgres_container):
    """Create a fresh database schema for each test to ensure isolation."""
    # Swap the default driver in the URL for our installed psycopg driver
    raw_url = postgres_container.get_connection_url()
    # Explicitly catch and replace psycopg2 with psycopg
    url = raw_url.replace("psycopg2", "psycopg").replace("postgresql://", "postgresql+psycopg://")
    
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield SessionLocal
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session_factory):
    """Provide a TestClient that uses the temporary database."""
    with TestClient(app) as test_client:
        # Override app.state AFTER lifespan runs so tests never touch the local DB
        app.state.member_service = DatabaseMemberService(db_session_factory)
        app.state.book_service = DatabaseBookService(db_session_factory)
        yield test_client

@pytest.fixture
def admin_headers():
    return {"Authorization": f"Bearer {settings.admin_token}"}

@pytest.fixture
def member_headers():
    return {"Authorization": f"Bearer {settings.member_token}"}