"""FastAPI application for the Library Management System API."""

from fastapi import FastAPI

from app.routers.books import router as books_router
from app.routers.members import router as members_router

tags_metadata = [
    {
        "name": "General",
        "description": "Basic application information and health checks.",
    },
    {
        "name": "Members",
        "description": "Create and manage library members and view their borrowed books.",
    },
    {
        "name": "Books",
        "description": "Create and manage books that are borrowed by members.",
    },
]

app = FastAPI(
    title="Library Management System API",
    description=(
        "Manage library members and their borrowed books. Assignment 1 API "
        "demonstrating FastAPI routes, Pydantic validation, and OpenAPI contracts."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
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