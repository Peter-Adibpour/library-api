"""Abstract service contracts for the Library API."""

from abc import ABC, abstractmethod

class MemberServiceAbstraction(ABC):
    @abstractmethod
    def get_members(self):
        pass

    @abstractmethod
    def get_member_by_id(self, member_id: int):
        pass

    @abstractmethod
    def get_member_books(self, member_id: int):
        pass

    @abstractmethod
    def create_member(self, data):
        pass

    @abstractmethod
    def replace_member(self, member_id: int, data):
        pass

    @abstractmethod
    def delete_member(self, member_id: int):
        pass

class BookServiceAbstraction(ABC):
    @abstractmethod
    def get_books(self):
        pass

    @abstractmethod
    def get_book_by_id(self, book_id: int):
        pass

    @abstractmethod
    def create_book(self, data):
        pass

    @abstractmethod
    def replace_book(self, book_id: int, data):
        pass

    @abstractmethod
    def delete_book(self, book_id: int):
        pass