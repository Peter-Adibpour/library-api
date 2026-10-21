"""Database repository layer for executing SQLAlchemy queries."""

from sqlalchemy.orm import Session
from app.models import Member, Book

class MemberRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(Member).all()

    def get_by_id(self, member_id: int):
        return self.session.query(Member).filter(Member.id == member_id).first()

    def get_by_email_or_membership(self, email: str, membership_id: str):
        return self.session.query(Member).filter(
            (Member.email == email) | (Member.membership_id == membership_id)
        ).first()

    def add(self, member: Member):
        self.session.add(member)

    def delete(self, member: Member):
        self.session.delete(member)

class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(Book).all()

    def get_by_id(self, book_id: int):
        return self.session.query(Book).filter(Book.id == book_id).first()

    def get_by_isbn(self, isbn: str):
        return self.session.query(Book).filter(Book.isbn == isbn).first()

    def add(self, book: Book):
        self.session.add(book)

    def delete(self, book: Book):
        self.session.delete(book)