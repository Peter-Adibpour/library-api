"""In-memory implementation of the Library services."""

from app.services.interfaces import MemberServiceAbstraction, BookServiceAbstraction
from app.schemas.members import MemberResponse
from app.schemas.books import BookResponse
from app.exceptions import ResourceNotFoundError, DuplicateResourceError, BusinessRuleError
from app.storage import members, books


class InMemoryMemberService(MemberServiceAbstraction):
    def get_members(self):
        return members

    def get_member_by_id(self, member_id: int):
        for member in members:
            if member.id == member_id:
                return member
        raise ResourceNotFoundError(f"Member {member_id} not found")

    def get_member_books(self, member_id: int):
        self.get_member_by_id(member_id)
        return [book for book in books if book.member_id == member_id]

    def create_member(self, data):
        for member in members:
            if member.email == data.email or member.membership_id == data.membership_id:
                raise DuplicateResourceError("Email or Membership ID already exists")

        next_id = max((m.id for m in members), default=0) + 1
        new_member = MemberResponse(id=next_id, **data.model_dump())
        members.append(new_member)
        return new_member

    def replace_member(self, member_id: int, data):
        target_member = self.get_member_by_id(member_id)

        for member in members:
            if member.id != member_id:
                if member.email == data.email or member.membership_id == data.membership_id:
                    raise DuplicateResourceError("Email or Membership ID already exists")

        updated_member = MemberResponse(id=member_id, **data.model_dump())
        members[members.index(target_member)] = updated_member
        return updated_member

    def delete_member(self, member_id: int):
        target_member = self.get_member_by_id(member_id)
        if any(book.member_id == member_id for book in books):
            raise BusinessRuleError("Cannot delete member with associated books")
        members.remove(target_member)


class InMemoryBookService(BookServiceAbstraction):
    def get_books(self):
        return books

    def get_book_by_id(self, book_id: int):
        for book in books:
            if book.id == book_id:
                return book
        raise ResourceNotFoundError(f"Book {book_id} not found")

    def create_book(self, data):
        if not any(member.id == data.member_id for member in members):
            raise ResourceNotFoundError("Associated member does not exist")

        for book in books:
            if book.isbn == data.isbn:
                raise DuplicateResourceError("ISBN already exists")

        next_id = max((b.id for b in books), default=0) + 1
        new_book = BookResponse(id=next_id, **data.model_dump())
        books.append(new_book)
        return new_book

    def replace_book(self, book_id: int, data):
        target_book = self.get_book_by_id(book_id)

        if not any(member.id == data.member_id for member in members):
            raise ResourceNotFoundError("Associated member does not exist")

        for book in books:
            if book.id != book_id and book.isbn == data.isbn:
                raise DuplicateResourceError("ISBN already exists")

        updated_book = BookResponse(id=book_id, **data.model_dump())
        books[books.index(target_book)] = updated_book
        return updated_book

    def delete_book(self, book_id: int):
        target_book = self.get_book_by_id(book_id)
        books.remove(target_book)