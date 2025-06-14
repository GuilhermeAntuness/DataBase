from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.book import Book, BookCopy
from database import get_db

router = APIRouter(prefix="/books")

# Request and Response Models
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True

class BookCopyBase(BaseModel):
    copy_number: int
    condition: Optional[str] = None
    location: Optional[str] = None

class BookCopyCreate(BookCopyBase):
    book_id: int

class BookCopyResponse(BookCopyBase):
    id: int
    book_id: int
    is_available: bool

    class Config:
        from_attributes = True

# Routes
@router.post("/", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookResponse])
def list_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    update_data = book.model_dump()
    for key, value in update_data.items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(book)
    db.commit()
    return {"message": "Livro deletado com sucesso"}

# Book Copy Routes
@router.post("/copies/", response_model=BookCopyResponse)
def create_book_copy(copy: BookCopyCreate, db: Session = Depends(get_db)):
    # Verificar se o livro existe
    book = db.query(Book).filter(Book.id == copy.book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db_copy = BookCopy(
        book_id=copy.book_id,
        copy_number=copy.copy_number,
        condition=copy.condition,
        location=copy.location,
        is_available=True
    )
    db.add(db_copy)
    db.commit()
    db.refresh(db_copy)
    return db_copy

@router.get("/copies/", response_model=List[BookCopyResponse])
def list_book_copies(db: Session = Depends(get_db)):
    copies = db.query(BookCopy).all()
    return copies

@router.get("/copies/{copy_id}", response_model=BookCopyResponse)
def get_book_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    return copy

@router.put("/copies/{copy_id}", response_model=BookCopyResponse)
def update_book_copy(copy_id: int, copy: BookCopyBase, db: Session = Depends(get_db)):
    db_copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if db_copy is None:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    
    update_data = copy.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_copy, key, value)
    
    db.commit()
    db.refresh(db_copy)
    return db_copy

@router.delete("/copies/{copy_id}")
def delete_book_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    
    db.delete(copy)
    db.commit()
    return {"message": "Cópia do livro deletada com sucesso"} 