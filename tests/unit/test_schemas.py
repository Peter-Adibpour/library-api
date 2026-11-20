import pytest
from pydantic import ValidationError
from app.schemas.members import MemberInput
from app.schemas.books import BookInput


def test_member_input_valid():
    member = MemberInput(
        name="Jane Doe",
        email="jane@example.com",
        membership_id="MEM-1",
        phone="+15551234567",
    )
    assert member.name == "Jane Doe"
    assert member.email == "jane@example.com"


def test_member_input_trims_whitespace():
    member = MemberInput(
        name="  Jane Doe  ",
        email="jane@example.com",
        membership_id="  MEM-1  ",
        phone="+15551234567",
    )
    assert member.name == "Jane Doe"
    assert member.membership_id == "MEM-1"


def test_member_input_missing_required_fields():
    with pytest.raises(ValidationError):
        MemberInput(name="Jane Doe")


def test_member_input_invalid_email():
    with pytest.raises(ValidationError):
        MemberInput(
            name="Jane Doe",
            email="not-an-email",
            membership_id="MEM-1",
            phone="+15551234567",
        )


def test_member_input_invalid_phone():
    with pytest.raises(ValidationError):
        MemberInput(
            name="Jane Doe",
            email="jane@example.com",
            membership_id="MEM-1",
            phone="555-1234",
        )


def test_member_input_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        MemberInput(
            name="Jane Doe",
            email="jane@example.com",
            membership_id="MEM-1",
            phone="+15551234567",
            extra_field="not-allowed",
        )


def test_book_input_valid():
    book = BookInput(
        title="Test Book",
        author="Author Name",
        isbn="978-0132350884",
        published_year=2020,
        member_id=1,
    )
    assert book.title == "Test Book"
    assert book.published_year == 2020


def test_book_input_trims_whitespace():
    book = BookInput(
        title="  Clean Code  ",
        author="  Robert C. Martin  ",
        isbn="  978-0132350884  ",
        published_year=2008,
        member_id=1,
    )
    assert book.title == "Clean Code"
    assert book.author == "Robert C. Martin"
    assert book.isbn == "978-0132350884"


def test_book_input_missing_required_fields():
    with pytest.raises(ValidationError):
        BookInput(title="Test Book")


@pytest.mark.parametrize("bad_year", [1000, 1449, 2200, -5])
def test_book_input_invalid_published_year(bad_year):
    with pytest.raises(ValidationError):
        BookInput(
            title="Test Book",
            author="Author",
            isbn="978-0132350884",
            published_year=bad_year,
            member_id=1,
        )


def test_book_input_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        BookInput(
            title="Test Book",
            author="Author",
            isbn="978-0132350884",
            published_year=2020,
            member_id=1,
            unexpected="nope",
        )