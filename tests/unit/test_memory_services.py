import pytest
from app.services.memory import InMemoryMemberService, InMemoryBookService
from app.schemas.members import MemberInput
from app.schemas.books import BookInput
from app.exceptions import ResourceNotFoundError, DuplicateResourceError, BusinessRuleError
from app.storage import members, books


@pytest.fixture(autouse=True)
def clear_memory_storage():
    members.clear()
    books.clear()
    yield
    members.clear()
    books.clear()


def test_memory_member_crud_and_duplicate_checks():
    service = InMemoryMemberService()
    data = MemberInput(
        name="Alice",
        email="alice@example.com",
        membership_id="MEM-1",
        phone="+15551234567",
    )
    created = service.create_member(data)
    assert created.id == 1
    assert service.get_member_by_id(1).email == "alice@example.com"

    with pytest.raises(DuplicateResourceError):
        service.create_member(data)

    with pytest.raises(ResourceNotFoundError):
        service.get_member_by_id(999)


def test_memory_book_relationship_and_blocked_member_deletion():
    member_service = InMemoryMemberService()
    book_service = InMemoryBookService()

    member = member_service.create_member(
        MemberInput(
            name="Alice",
            email="alice@example.com",
            membership_id="MEM-1",
            phone="+15551234567",
        )
    )

    with pytest.raises(ResourceNotFoundError):
        book_service.create_book(
            BookInput(
                title="Orphan",
                author="Nobody",
                isbn="978-0132350884",
                published_year=2020,
                member_id=999,
            )
        )

    book = book_service.create_book(
        BookInput(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="978-0132350884",
            published_year=2008,
            member_id=member.id,
        )
    )
    assert len(member_service.get_member_books(member.id)) == 1

    with pytest.raises(BusinessRuleError):
        member_service.delete_member(member.id)

    book_service.delete_book(book.id)
    member_service.delete_member(member.id)
    assert member_service.get_members() == []