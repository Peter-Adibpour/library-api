"""Database-backed implementation of the Library services."""

from app.services.interfaces import MemberServiceAbstraction, BookServiceAbstraction
from app.repositories import MemberRepository, BookRepository
from app.models import Member, Book
from app.exceptions import ResourceNotFoundError, DuplicateResourceError, BusinessRuleError

class DatabaseMemberService(MemberServiceAbstraction):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_members(self):
        with self.session_factory() as session:
            repo = MemberRepository(session)
            return repo.get_all()

    def get_member_by_id(self, member_id: int):
        with self.session_factory() as session:
            repo = MemberRepository(session)
            member = repo.get_by_id(member_id)
            if not member:
                raise ResourceNotFoundError(f"Member {member_id} not found")
            return member

    def get_member_books(self, member_id: int):
        with self.session_factory() as session:
            repo = MemberRepository(session)
            member = repo.get_by_id(member_id)
            if not member:
                raise ResourceNotFoundError(f"Member {member_id} not found")
            return member.books

    def create_member(self, data):
        with self.session_factory() as session:
            repo = MemberRepository(session)
            if repo.get_by_email_or_membership(data.email, data.membership_id):
                raise DuplicateResourceError("Email or Membership ID already exists")

            new_member = Member(**data.model_dump())
            
            try:
                repo.add(new_member)
                session.commit()
                session.refresh(new_member)
                return new_member
            except Exception as e:
                session.rollback()
                raise e

    def replace_member(self, member_id: int, data):
        with self.session_factory() as session:
            repo = MemberRepository(session)
            member = repo.get_by_id(member_id)
            if not member:
                raise ResourceNotFoundError(f"Member {member_id} not found")
            
            existing = repo.get_by_email_or_membership(data.email, data.membership_id)
            if existing and existing.id != member_id:
                raise DuplicateResourceError("Email or Membership ID already exists")

            for key, value in data.model_dump().items():
                setattr(member, key, value)
            
            try:
                session.commit()
                session.refresh(member)
                return member
            except Exception as e:
                session.rollback()
                raise e

    def delete_member(self, member_id: int):
        with self.session_factory() as session:
            repo = MemberRepository(session)
            member = repo.get_by_id(member_id)
            if not member:
                raise ResourceNotFoundError(f"Member {member_id} not found")
            if member.books:
                raise BusinessRuleError("Cannot delete member with associated books")
                
            try:
                repo.delete(member)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

class DatabaseBookService(BookServiceAbstraction):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_books(self):
        with self.session_factory() as session:
            repo = BookRepository(session)
            return repo.get_all()

    def get_book_by_id(self, book_id: int):
        with self.session_factory() as session:
            repo = BookRepository(session)
            book = repo.get_by_id(book_id)
            if not book:
                raise ResourceNotFoundError(f"Book {book_id} not found")
            return book

    def create_book(self, data):
        with self.session_factory() as session:
            member_repo = MemberRepository(session)
            book_repo = BookRepository(session)
            
            if not member_repo.get_by_id(data.member_id):
                raise ResourceNotFoundError("Associated member does not exist")
            
            if book_repo.get_by_isbn(data.isbn):
                raise DuplicateResourceError("ISBN already exists")

            new_book = Book(**data.model_dump())
            
            try:
                book_repo.add(new_book)
                session.commit()
                session.refresh(new_book)
                return new_book
            except Exception as e:
                session.rollback()
                raise e

    def replace_book(self, book_id: int, data):
        with self.session_factory() as session:
            member_repo = MemberRepository(session)
            book_repo = BookRepository(session)
            
            book = book_repo.get_by_id(book_id)
            if not book:
                raise ResourceNotFoundError(f"Book {book_id} not found")
                
            if not member_repo.get_by_id(data.member_id):
                raise ResourceNotFoundError("Associated member does not exist")
                
            existing_isbn = book_repo.get_by_isbn(data.isbn)
            if existing_isbn and existing_isbn.id != book_id:
                raise DuplicateResourceError("ISBN already exists")

            for key, value in data.model_dump().items():
                setattr(book, key, value)
            
            try:
                session.commit()
                session.refresh(book)
                return book
            except Exception as e:
                session.rollback()
                raise e

    def delete_book(self, book_id: int):
        with self.session_factory() as session:
            repo = BookRepository(session)
            book = repo.get_by_id(book_id)
            if not book:
                raise ResourceNotFoundError(f"Book {book_id} not found")
                
            try:
                repo.delete(book)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e