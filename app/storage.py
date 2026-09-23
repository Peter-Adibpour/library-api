"""In-memory storage for the Library Management System API."""

from app.schemas.books import BookResponse
from app.schemas.members import MemberResponse

# Temporary collections to hold data until database persistence is introduced.
members: list[MemberResponse] = []
books: list[BookResponse] = []