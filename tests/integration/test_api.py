def test_create_member_admin_success(client, admin_headers):
    response = client.post(
        "/members", 
        json={"name": "Alice", "email": "alice@example.com", "membership_id": "M1", "phone": "123"},
        headers=admin_headers
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"

def test_create_member_member_role_forbidden(client, member_headers):
    response = client.post(
        "/members", 
        json={"name": "Bob", "email": "bob@example.com", "membership_id": "M2", "phone": "123"},
        headers=member_headers
    )
    assert response.status_code == 403

def test_unauthorized_missing_token(client):
    response = client.get("/members")
    assert response.status_code == 401

def test_get_members_success(client, admin_headers, member_headers):
    # Admin creates a member
    client.post(
        "/members", 
        json={"name": "Alice", "email": "a@example.com", "membership_id": "M1", "phone": "123"},
        headers=admin_headers
    )
    
    # Member role can successfully retrieve the list
    response = client.get("/members", headers=member_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_create_book_missing_member(client, admin_headers):
    response = client.post(
        "/books",
        json={"title": "Test", "author": "Test", "isbn": "123", "published_year": 2020, "member_id": 999},
        headers=admin_headers
    )
    assert response.status_code == 404

VALID_MEMBER = {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "membership_id": "MEM-001",
    "phone": "+15551234567",
}

VALID_MEMBER_2 = {
    "name": "Bob Jones",
    "email": "bob@example.com",
    "membership_id": "MEM-002",
    "phone": "+15557654321",
}


def make_book(member_id: int, isbn: str = "978-0132350884", title: str = "Clean Code"):
    return {
        "title": title,
        "author": "Robert C. Martin",
        "isbn": isbn,
        "published_year": 2008,
        "member_id": member_id,
    }


# --- Public vs. Protected Access & Auth ---

def test_public_endpoints_accessible_without_token(client):
    for path in ("/", "/health", "/docs", "/openapi.json"):
        response = client.get(path)
        assert response.status_code == 200


def test_unauthorized_missing_token_returns_401_with_bearer_challenge(client):
    response = client.get("/members")
    assert response.status_code == 401
    assert "bearer" in response.headers.get("www-authenticate", "").lower()


def test_unauthorized_invalid_and_malformed_tokens(client):
    bad_headers = [
        {"Authorization": "Bearer totally-wrong-token"},
        {"Authorization": "Basic dXNlcjpwYXNz"},
    ]
    for headers in bad_headers:
        response = client.get("/members", headers=headers)
        assert response.status_code == 401
        assert "bearer" in response.headers.get("www-authenticate", "").lower()


def test_member_role_cannot_write_and_data_stays_unchanged(client, admin_headers, member_headers):
    # Create a member as admin first
    created = client.post("/members", json=VALID_MEMBER, headers=admin_headers).json()

    # Member role is forbidden from POST, PUT, DELETE
    assert client.post("/members", json=VALID_MEMBER_2, headers=member_headers).status_code == 403
    assert client.put(f"/members/{created['id']}", json=VALID_MEMBER_2, headers=member_headers).status_code == 403
    assert client.delete(f"/members/{created['id']}", headers=member_headers).status_code == 403

    # Verify stored data was not modified
    members = client.get("/members", headers=member_headers).json()
    assert len(members) == 1
    assert members[0]["email"] == VALID_MEMBER["email"]


# --- Happy-Path CRUD & Related-Book Workflows ---

def test_member_and_book_full_workflow(client, admin_headers, member_headers):
    # Create Member
    m_res = client.post("/members", json=VALID_MEMBER, headers=admin_headers)
    assert m_res.status_code == 201
    member_id = m_res.json()["id"]

    # Member role can read Member
    get_m = client.get(f"/members/{member_id}", headers=member_headers)
    assert get_m.status_code == 200
    assert get_m.json()["email"] == VALID_MEMBER["email"]

    # Create Book for Member
    b_res = client.post("/books", json=make_book(member_id), headers=admin_headers)
    assert b_res.status_code == 201
    book_id = b_res.json()["id"]

    # Retrieve Member's Books via nested route
    nested = client.get(f"/members/{member_id}/books", headers=member_headers)
    assert nested.status_code == 200
    assert len(nested.json()) == 1
    assert nested.json()[0]["id"] == book_id

    # Replace Book
    updated_payload = make_book(member_id, title="Clean Architecture")
    put_b = client.put(f"/books/{book_id}", json=updated_payload, headers=admin_headers)
    assert put_b.status_code == 200
    assert put_b.json()["title"] == "Clean Architecture"

    # Delete Book, then Delete Member
    assert client.delete(f"/books/{book_id}", headers=admin_headers).status_code == 204
    assert client.delete(f"/members/{member_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/members/{member_id}", headers=member_headers).status_code == 404


# --- Explicit HTTP Negative Validation Tests (422) ---

def test_negative_missing_required_field_returns_422_detail(client, admin_headers):
    response = client.post("/members", json={"name": "Incomplete"}, headers=admin_headers)
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body and isinstance(body["detail"], list)
    missing_fields = {err["loc"][-1] for err in body["detail"]}
    assert {"email", "membership_id", "phone"}.issubset(missing_fields)


def test_negative_unknown_json_field_returns_422(client, admin_headers):
    payload = {**VALID_MEMBER, "unexpected_field": "boom"}
    response = client.post("/members", json=payload, headers=admin_headers)
    assert response.status_code == 422
    assert any(err["loc"][-1] == "unexpected_field" for err in response.json()["detail"])


def test_negative_invalid_field_boundary_returns_422(client, admin_headers):
    member_id = client.post("/members", json=VALID_MEMBER, headers=admin_headers).json()["id"]
    bad_book = {**make_book(member_id), "published_year": 1200}
    response = client.post("/books", json=bad_book, headers=admin_headers)
    assert response.status_code == 422
    assert any(err["loc"][-1] == "published_year" for err in response.json()["detail"])


def test_negative_invalid_path_id_type_returns_422(client, member_headers):
    response = client.get("/members/not-an-integer", headers=member_headers)
    assert response.status_code == 422
    assert any(err["loc"][-1] == "member_id" for err in response.json()["detail"])


# --- Explicit Business-Rule & Conflict Tests (404 / 409) ---

def test_missing_member_and_book_return_404(client, member_headers):
    assert client.get("/members/999", headers=member_headers).status_code == 404
    assert client.get("/members/999/books", headers=member_headers).status_code == 404
    assert client.get("/books/999", headers=member_headers).status_code == 404


def test_create_book_with_nonexistent_member_returns_404(client, admin_headers):
    response = client.post("/books", json=make_book(999), headers=admin_headers)
    assert response.status_code == 404
    assert client.get("/books", headers=admin_headers).json() == []


def test_duplicate_email_membership_and_isbn_return_409_without_corrupting_data(client, admin_headers):
    m1 = client.post("/members", json=VALID_MEMBER, headers=admin_headers).json()

    # Duplicate email
    dup_email = {**VALID_MEMBER_2, "email": VALID_MEMBER["email"]}
    assert client.post("/members", json=dup_email, headers=admin_headers).status_code == 409

    # Duplicate membership_id
    dup_mid = {**VALID_MEMBER_2, "membership_id": VALID_MEMBER["membership_id"]}
    assert client.post("/members", json=dup_mid, headers=admin_headers).status_code == 409

    # Stored members count is still 1
    assert len(client.get("/members", headers=admin_headers).json()) == 1

    # Create book, then attempt duplicate ISBN
    assert client.post("/books", json=make_book(m1["id"]), headers=admin_headers).status_code == 201
    assert client.post("/books", json=make_book(m1["id"], title="Other"), headers=admin_headers).status_code == 409
    assert len(client.get("/books", headers=admin_headers).json()) == 1


def test_delete_member_with_books_blocked_with_409_and_preserves_data(client, admin_headers):
    member_id = client.post("/members", json=VALID_MEMBER, headers=admin_headers).json()["id"]
    book_id = client.post("/books", json=make_book(member_id), headers=admin_headers).json()["id"]

    res = client.delete(f"/members/{member_id}", headers=admin_headers)
    assert res.status_code == 409

    # Both member and book still exist intact
    assert client.get(f"/members/{member_id}", headers=admin_headers).status_code == 200
    assert client.get(f"/books/{book_id}", headers=admin_headers).status_code == 200