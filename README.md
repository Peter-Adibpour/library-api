# Library Management System API

A FastAPI REST API for managing Library Members and Books, featuring a layered architecture (routers, service abstractions, repositories, and SQLAlchemy ORM models), dual storage backends (PostgreSQL and in-memory), classroom Bearer token role-based access control, and an automated unit, integration, and OpenAPI conformance test suite.

## Architecture Overview

The application separates HTTP handling, business logic, and persistence into distinct layers:

- Routers (app/routers/): Handle HTTP requests, dependency injection, Bearer authentication/authorization, and map domain exceptions to HTTP status codes (401, 403, 404, 409, 422).

- Services (app/services/): Implement shared service abstractions (MemberServiceAbstraction, BookServiceAbstraction) for both PostgreSQL and in-memory backends, keeping business rules independent of HTTP credentials.

- Repositories & ORM Models (app/repositories.py, app/models.py): Encapsulate SQLAlchemy queries, database constraints, and transactions.

Flat Layout Note: This project uses a flat app/ directory layout rather than nested API-version packages to keep module imports concise while preserving strict layer boundaries.

## Prerequisites

- Python 3.12+

- uv (Python package and environment manager)

- PostgreSQL (required only when running the API locally with STORAGE_BACKEND=database)

- Docker Desktop (required to run Testcontainers PostgreSQL integration tests)

## Setup from a Clean Checkout

Clone the repository and switch to the required branch:

```bash
git checkout assignment-3
```

Install all runtime and development dependencies from pyproject.toml and uv.lock:

```bash
uv sync
```

Create your local environment file from the safe template:

```bash
cp .env.example .env
```

Update DATABASE_URL in .env if your local PostgreSQL username, password, or port differs from the default placeholder. Never commit your .env file.

## Database Initialization (PostgreSQL Backend)

Before starting the API against a fresh PostgreSQL database, create the database and initialize the tables:

Create the empty database in PostgreSQL (for example, using psql):

```sql
CREATE DATABASE library; 
```

Create the members and books tables from the SQLAlchemy models:

```bash
uv run python -c "from app.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
```

Note: To run the API without PostgreSQL, set STORAGE_BACKEND=memory in your .env file.

## Running the API

Start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

### Public Endpoints & Interactive Documentation

The following routes are public and do not require a Bearer token:

- Root: <http://127.0.0.1:8000/>

- Health Check: <http://127.0.0.1:8000/health>

- Swagger UI: <http://127.0.0.1:8000/docs>

- ReDoc: <http://127.0.0.1:8000/redoc>

- OpenAPI Schema: <http://127.0.0.1:8000/openapi.json>

## Authentication & Example Bearer Requests

All `/members` and `/books` endpoints require an HTTP Bearer token:

- Member Role (`MEMBER_TOKEN`): Read-only access (GET requests). Write attempts return 403 Forbidden.

- Administrator Role (`ADMIN_TOKEN`): Full read and write access (GET, POST, PUT, DELETE).

Missing, malformed, or unknown tokens return `401 Unauthorized` with a WWW-Authenticate: Bearer header.

### 1. Public Health Check (No Token)

```bash
curl http://127.0.0.1:8000/health
```

### 2. Create a Member (Admin Token Required -> 201 Created)

```bash
curl -X POST http://127.0.0.1:8000/members \
  -H "Authorization: Bearer instructor-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com", "membership_id": "MEM-001", "phone": "+15551234567"}'
```

### 3. List Members (Member Token Allowed -> 200 OK)

```bash
curl http://127.0.0.1:8000/members \
  -H "Authorization: Bearer student-member-token"
```

### 4. Member Role Attempting a Write (Denied -> 403 Forbidden)

```bash
curl -X DELETE http://127.0.0.1:8000/members/1 \
  -H "Authorization: Bearer student-member-token"
```

### 5. Create a Book and Retrieve a Member's Books

```bash
# Create:

curl -X POST http://127.0.0.1:8000/books \
  -H "Authorization: Bearer instructor-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin", "isbn": "978-0132350884", "published_year": 2008, "member_id": 1}'

# Retrieve:

curl http://127.0.0.1:8000/members/1/books \
  -H "Authorization: Bearer student-member-token"
```

You can also click the Authorize button in Swagger UI (/docs) and paste either classroom token to test protected routes interactively.

## Running the Automated Tests

### Docker & Testcontainers Requirement

Make sure Docker Desktop is running before executing the full test suite. Integration tests use Testcontainers to spin up a disposable postgres:16-alpine container for the test session and recreate clean tables for every test function. The test suite never connects to or modifies your local PostgreSQL library database.

### Test Commands

Run the complete test suite (unit, integration, negative, security, and OpenAPI conformance tests):

```bash
uv run python -m pytest
```

Run individual test layers:

```bash
# Isolated unit tests (schemas, auth, mocked DB services, in-memory services — no Docker required)

uv run python -m pytest tests/unit/

# Integration tests (Testcontainers PostgreSQL repositories, API workflows, negative rules, and in-memory API)

uv run python -m pytest tests/integration/

# OpenAPI specification validation and Schemathesis conformance tests

uv run python -m pytest tests/conformance/
```

## Project Structure

```text
├── app/ 
│   ├── routers/ 
│   │   ├── books.py                # Book HTTP endpoints, role checks, exception mapping 
│   │   └── members.py              # Member & nested Member-Books endpoints 
│   ├── schemas/ 
│   │   ├── books.py                # Book Pydantic input/response validation models 
│   │   └── members.py              # Member Pydantic input/response validation models 
│   ├── services/ 
│   │   ├── database.py             # PostgreSQL-backed service implementations 
│   │   ├── interfaces.py           # Abstract service contracts 
│   │   └── memory.py               # In-memory service implementations 
│   ├── auth.py                     # HTTPBearer token authentication and role dependencies 
│   ├── config.py                   # Typed Pydantic settings (.env loader) 
│   ├── database.py                 # SQLAlchemy engine, Base, and session factory 
│   ├── exceptions.py               # Application-specific domain exceptions 
│   ├── main.py                     # FastAPI app, lifespan backend selection, public routes 
│   ├── models.py                   # SQLAlchemy Member and Book ORM models 
│   ├── repositories.py             # MemberRepository and BookRepository data access 
│   └── storage.py                  # In-memory storage lists 
├── tests/ 
│   ├── conformance/ 
│   │   └── test_openapi.py         # OpenAPI spec validation & Schemathesis conformance 
│   ├── integration/ 
│   │   ├── test_api.py             # PostgreSQL API, auth, negative, and business-rule tests 
│   │   ├── test_memory_api.py      # In-memory backend API integration tests 
│   │   └── test_repositories.py    # Direct ORM/PostgreSQL constraint tests 
│   ├── unit/ 
│   │   ├── test_auth.py            # Token-to-role mapping and 401/403 unit tests 
│   │   ├── test_memory_services.py # In-memory service unit tests 
│   │   ├── test_schemas.py         # Pydantic boundary, trimming, and unknown-field tests 
│   │   └── test_services.py        # Mocked DatabaseMemberService & DatabaseBookService tests 
│   └── conftest.py                 # Testcontainers PostgreSQL and TestClient fixtures 
├── .env.example                    # Safe template for storage and classroom token settings 
├── pyproject.toml                  # Project dependencies and pytest configuration 
├── uv.lock                         # Locked dependency versions 
└── README.md                       # Setup, usage, and testing guide
```
