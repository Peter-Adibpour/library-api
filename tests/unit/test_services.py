import pytest
from unittest.mock import MagicMock, patch
from app.services.database import DatabaseMemberService, DatabaseBookService
from app.exceptions import ResourceNotFoundError, DuplicateResourceError, BusinessRuleError
from app.schemas.members import MemberInput
from app.schemas.books import BookInput
from app.models import Member, Book


@pytest.fixture
def mock_session_factory():
    session = MagicMock()
    session.__enter__.return_value = session
    factory = MagicMock(return_value=session)
    return factory, session


# --- DatabaseMemberService ---

def test_get_member_by_id_success(mock_session_factory):
    factory, _ = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        expected = Member(id=1, name="Jane")
        MockRepo.return_value.get_by_id.return_value = expected
        assert service.get_member_by_id(1) is expected


def test_get_member_by_id_not_found(mock_session_factory):
    factory, _ = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        MockRepo.return_value.get_by_id.return_value = None
        with pytest.raises(ResourceNotFoundError):
            service.get_member_by_id(999)


def test_get_member_books_not_found(mock_session_factory):
    factory, _ = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        MockRepo.return_value.get_by_id.return_value = None
        with pytest.raises(ResourceNotFoundError):
            service.get_member_books(999)


def test_create_member_success_commits(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        MockRepo.return_value.get_by_email_or_membership.return_value = None
        data = MemberInput(
            name="Jane Doe",
            email="jane@example.com",
            membership_id="MEM-1",
            phone="+15551234567",
        )
        result = service.create_member(data)
        assert result.email == "jane@example.com"
        session.commit.assert_called_once()
        session.refresh.assert_called_once()


def test_create_member_duplicate(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        MockRepo.return_value.get_by_email_or_membership.return_value = Member(id=1)
        data = MemberInput(
            name="Test",
            email="duplicate@example.com",
            membership_id="MEM-1",
            phone="+15551234567",
        )
        with pytest.raises(DuplicateResourceError):
            service.create_member(data)
        session.commit.assert_not_called()


def test_delete_member_with_books_blocked(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        mock_member = MagicMock()
        mock_member.books = [MagicMock()]
        MockRepo.return_value.get_by_id.return_value = mock_member

        with pytest.raises(BusinessRuleError, match="Cannot delete member with associated books"):
            service.delete_member(1)
        session.commit.assert_not_called()


def test_delete_member_without_books_commits(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseMemberService(factory)

    with patch("app.services.database.MemberRepository") as MockRepo:
        mock_member = MagicMock()
        mock_member.books = []
        MockRepo.return_value.get_by_id.return_value = mock_member

        service.delete_member(1)
        MockRepo.return_value.delete.assert_called_once_with(mock_member)
        session.commit.assert_called_once()


# --- DatabaseBookService ---

def test_get_book_by_id_not_found(mock_session_factory):
    factory, _ = mock_session_factory
    service = DatabaseBookService(factory)

    with patch("app.services.database.BookRepository") as MockBookRepo:
        MockBookRepo.return_value.get_by_id.return_value = None
        with pytest.raises(ResourceNotFoundError):
            service.get_book_by_id(999)


def test_create_book_missing_member_raises_not_found(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseBookService(factory)

    with (
        patch("app.services.database.MemberRepository") as MockMemberRepo,
        patch("app.services.database.BookRepository"),
    ):
        MockMemberRepo.return_value.get_by_id.return_value = None
        data = BookInput(
            title="Test",
            author="Author",
            isbn="978-0132350884",
            published_year=2020,
            member_id=999,
        )
        with pytest.raises(ResourceNotFoundError):
            service.create_book(data)
        session.commit.assert_not_called()


def test_create_book_duplicate_isbn_raises_conflict(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseBookService(factory)

    with (
        patch("app.services.database.MemberRepository") as MockMemberRepo,
        patch("app.services.database.BookRepository") as MockBookRepo,
    ):
        MockMemberRepo.return_value.get_by_id.return_value = Member(id=1)
        MockBookRepo.return_value.get_by_isbn.return_value = Book(id=1)
        data = BookInput(
            title="Test",
            author="Author",
            isbn="978-0132350884",
            published_year=2020,
            member_id=1,
        )
        with pytest.raises(DuplicateResourceError):
            service.create_book(data)
        session.commit.assert_not_called()


def test_create_book_success_commits(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseBookService(factory)

    with (
        patch("app.services.database.MemberRepository") as MockMemberRepo,
        patch("app.services.database.BookRepository") as MockBookRepo,
    ):
        MockMemberRepo.return_value.get_by_id.return_value = Member(id=1)
        MockBookRepo.return_value.get_by_isbn.return_value = None
        data = BookInput(
            title="Test",
            author="Author",
            isbn="978-0132350884",
            published_year=2020,
            member_id=1,
        )
        result = service.create_book(data)
        assert result.isbn == "978-0132350884"
        session.commit.assert_called_once()


def test_delete_book_not_found(mock_session_factory):
    factory, session = mock_session_factory
    service = DatabaseBookService(factory)

    with patch("app.services.database.BookRepository") as MockBookRepo:
        MockBookRepo.return_value.get_by_id.return_value = None
        with pytest.raises(ResourceNotFoundError):
            service.delete_book(999)
        session.commit.assert_not_called()