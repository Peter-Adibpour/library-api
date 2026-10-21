from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    membership_id = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)

    books = relationship("Book", back_populates="member")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(120), nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=False)
    published_year = Column(Integer, nullable=False)
    
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    member = relationship("Member", back_populates="books")