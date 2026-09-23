# Library Management System API

The Library Management System API is a backend for managing library Members and their borrowed Books. Users can create, view, update, and delete both resources, and each Book is borrowed by exactly one Member. 

This repository contains the Assignment 1 submission for SDEV 3310.

## Assignment 1 scope

This API demonstrates:
- Treating Members and Books as related REST resources
- Using resource-oriented collection, item, and relationship URLs
- Enforcing Pydantic schemas with custom string stripping, bounds, and E.164 phone validation
- Documenting expected success and error responses (including 409 Conflicts for uniqueness)
- Storing temporary data in memory before database persistence is introduced

## Install project dependencies

Ensure `uv` is installed, then run:

```text
uv sync