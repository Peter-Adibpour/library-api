import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.memory import InMemoryMemberService, InMemoryBookService
from app.storage import members, books


@pytest.fixture
def memory_client():
    members.clear()
    books.clear()
    with TestClient(app) as test_client:
        app.state.member_service = InMemoryMemberService()
        app.state.book_service = InMemoryBookService()
        yield test_client
    members.clear()
    books.clear()


def test_memory_backend_api_workflow(memory_client, admin_headers, member_headers):
    m_res = memory_client.post(
        "/members",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "membership_id": "MEM-1",
            "phone": "+15551234567",
        },
        headers=admin_headers,
    )
    assert m_res.status_code == 201
    member_id = m_res.json()["id"]

    b_res = memory_client.post(
        "/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "978-0132350884",
            "published_year": 2008,
            "member_id": member_id,
        },
        headers=admin_headers,
    )
    assert b_res.status_code == 201

    nested = memory_client.get(f"/members/{member_id}/books", headers=member_headers)
    assert nested.status_code == 200
    assert len(nested.json()) == 1

    # Blocked deletion returns 409
    assert memory_client.delete(f"/members/{member_id}", headers=admin_headers).status_code == 409