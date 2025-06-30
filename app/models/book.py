from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    author = Column(String(128), nullable=False)
    isbn = Column(String(13), nullable=False, unique=True)
    publisher = Column(String(128), nullable=True)
    publication_year = Column(Integer, nullable=True)
    edition = Column(String(32), nullable=True)
    copies = relationship("BookCopy", back_populates="book")


class BookCopy(Base):
    __tablename__ = "book_copy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    copy_number = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    condition = Column(String(32), nullable=True)
    location = Column(String(64), nullable=True)
    
    book = relationship("Book", back_populates="copies") 