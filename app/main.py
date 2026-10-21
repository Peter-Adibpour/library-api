"""FastAPI application for the Library Management System API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from app.config import settings
from app.database import SessionLocal
from app.routers.members import router as members_router
from app.routers.books import router as books_router

# Import both sets of service implementations
from app.services.database import DatabaseMemberService, DatabaseBookService
from app.services.memory import InMemoryMemberService, InMemoryBookService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the selected storage backend at startup."""
    if settings.storage_backend == "database":
        # Pass the session factory to the database services
        app.state.member_service = DatabaseMemberService(SessionLocal)
        app.state.book_service = DatabaseBookService(SessionLocal)
    else:
        # Instantiate the temporary memory services
        app.state.member_service = InMemoryMemberService()
        app.state.book_service = InMemoryBookService()
    yield

app = FastAPI(
    title="Library Management System API",
    description="Assignment 2 API demonstrating layered design and PostgreSQL persistence.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(members_router)
app.include_router(books_router)

@app.get("/", tags=["General"], summary="Introduce the API")
def read_root() -> dict[str, str]:
    """Return a short introduction to the API."""
    return {"message": "Library Management System API"}

@app.get("/health", tags=["General"], summary="Check API health")
def health_check() -> dict[str, str]:
    """Confirm that the API process is running."""
    return {"status": "healthy"}