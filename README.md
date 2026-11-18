# Library Management System API

The Library Management System API is a backend for managing library Members and their borrowed Books. Users can create, view, update, and delete both resources, and each Book is borrowed by exactly one Member.

This repository contains the Assignment 2 submission, demonstrating a layered architectural design, dependency injection, and PostgreSQL persistence using SQLAlchemy.

## Architecture and Storage Backends

This API separates HTTP routing, business logic (Services), and database queries (Repositories) into distinct layers.

It supports two interchangeable storage backends configured via environment variables:

* `database`: (Default) Persists data to a PostgreSQL database using SQLAlchemy. Data survives application restarts.
* `memory`: Stores data in temporary Python lists. Data is lost when the application restarts.

## Prerequisites and Database Setup

1. Install [Python](https://www.python.org/) and [uv](https://docs.astral.sh/uv/).
2. Install [PostgreSQL](https://www.postgresql.org/) and ensure the service is running.
3. Create a local PostgreSQL database named `library` (or your preferred name).

## Configuration

1. Copy the example environment file to create your local configuration:
   `cp .env.example .env`
2. Open `.env` and update the `DATABASE_URL` with your local PostgreSQL username, password, and database name.
3. Ensure `STORAGE_BACKEND=database` is set to utilize PostgreSQL.

## Install project dependencies

Ensure `uv` is installed, then run:

```text
uv sync
```

## Run the API

Start the development server using Uvicorn:

```bash
uv run uvicorn app.main:app --reload
```

The server will run at <http://localhost:8000>.

## API Documentation

Once the server is running, explore the interactive OpenAPI documentation:

    Swagger UI: <http://localhost:8000/docs>

    ReDoc: http://localhost:8000/redoc

## Example Requests

1. Create a Member

POST /members
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "membership_id": "MEM-12345",
  "phone": "+15551234567"
}

2. Create a Book (Associated with the Member)

POST /books
Content-Type: application/json

{
  "title": "The REST API Design Rulebook",
  "author": "Mark Masse",
  "isbn": "978-1449310509",
  "published_year": 2011,
  "member_id": 1
}

## Current project structure

library-api/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── interfaces.py
│   │   └── memory.py
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── repositories.py
│   └── storage.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
