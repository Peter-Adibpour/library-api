import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Member, Book
from app.repositories import MemberRepository, BookRepository


def test_member_repository_generates_id_and_retrieves(db_session_factory):
    with db_session_factory() as session:
        repo = MemberRepository(session)
        member = Member(
            name="Alice",
            email="alice@example.com",
            membership_id="MEM-100",
            phone="+15551112222",
        )
        repo.add(member)
        session.commit()
        session.refresh(member)

        assert member.id is not None
        assert member.id >= 1
        fetched = repo.get_by_id(member.id)
        assert fetched is not None
        assert fetched.email == "alice@example.com"


def test_member_unique_email_constraint(db_session_factory):
    with db_session_factory() as session:
        repo = MemberRepository(session)
        repo.add(
            Member(
                name="Alice",
                email="dup@example.com",
                membership_id="MEM-1",
                phone="+15551112222",
            )
        )
        session.commit()

        repo.add(
            Member(
                name="Bob",
                email="dup@example.com",
                membership_id="MEM-2",
                phone="+15553334444",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_member_unique_membership_id_constraint(db_session_factory):
    with db_session_factory() as session:
        repo = MemberRepository(session)
        repo.add(
            Member(
                name="Alice",
                email="a@example.com",
                membership_id="MEM-DUP",
                phone="+15551112222",
            )
        )
        session.commit()

        repo.add(
            Member(
                name="Bob",
                email="b@example.com",
                membership_id="MEM-DUP",
                phone="+15553334444",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_book_unique_isbn_and_foreign_key_relationship(db_session_factory):
    with db_session_factory() as session:
        member_repo = MemberRepository(session)
        book_repo = BookRepository(session)

        member = Member(
            name="Alice",
            email="alice@example.com",
            membership_id="MEM-1",
            phone="+15551112222",
        )
        member_repo.add(member)
        session.commit()
        session.refresh(member)

        book1 = Book(
            title="Book One",
            author="Author One",
            isbn="978-0132350884",
            published_year=2008,
            member_id=member.id,
        )
        book_repo.add(book1)
        session.commit()
        session.refresh(book1)

        assert book1.id is not None
        assert len(member.books) == 1

        # Duplicate ISBN violates unique constraint
        book2 = Book(
            title="Book Two",
            author="Author Two",
            isbn="978-0132350884",
            published_year=2010,
            member_id=member.id,
        )
        book_repo.add(book2)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_book_foreign_key_rejects_nonexistent_member(db_session_factory):
    with db_session_factory() as session:
        book_repo = BookRepository(session)
        orphan_book = Book(
            title="Orphan",
            author="Nobody",
            isbn="978-0132350884",
            published_year=2020,
            member_id=99999,
        )
        book_repo.add(orphan_book)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()