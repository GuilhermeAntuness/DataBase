from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.book import Book, BookCopy
from database import get_db

router = APIRouter(prefix="/books", tags= ["Book"])

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

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None

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

class BookCopyUpdate(BaseModel):
    copy_number: Optional[int] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    is_available: Optional[bool] = None

# Book Routes
@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    # Verificar se já existe um livro com o mesmo ISBN
    book_existente = db.query(Book).filter(Book.isbn == book.isbn).first()
    if book_existente:
        raise HTTPException(status_code=400, detail="Já existe um livro com este ISBN")
    
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
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Se estiver atualizando o ISBN, verificar se já existe outro livro com o mesmo ISBN
    if book.isbn and book.isbn != db_book.isbn:
        book_existente = db.query(Book).filter(Book.isbn == book.isbn).first()
        if book_existente:
            raise HTTPException(status_code=400, detail="Já existe um livro com este ISBN")
    
    update_data = book.model_dump(exclude_unset=True)
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
    
    # Verificar se existem cópias vinculadas a este livro
    copies = db.query(BookCopy).filter(BookCopy.book_id == book_id).first()
    if copies:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível deletar este livro pois existem cópias vinculadas a ele"
        )
    
    db.delete(book)
    db.commit()
    return {"message": "Livro deletado com sucesso"}

@router.get("/isbn/{isbn}", response_model=BookResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

@router.get("/author/{author}", response_model=List[BookResponse])
def get_books_by_author(author: str, db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()
    return books

@router.get("/title/{title}", response_model=List[BookResponse])
def get_books_by_title(title: str, db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    return books

# Book Copy Routes
@router.post("/copies/",tags=["Book Copies"], response_model=BookCopyResponse, status_code=201)
def create_book_copy(copy: BookCopyCreate, db: Session = Depends(get_db)):
    # Verificar se o livro existe
    book = db.query(Book).filter(Book.id == copy.book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Verificar se já existe uma cópia com o mesmo número para este livro
    copy_existente = db.query(BookCopy).filter(
        BookCopy.book_id == copy.book_id,
        BookCopy.copy_number == copy.copy_number
    ).first()
    if copy_existente:
        raise HTTPException(
            status_code=400, 
            detail="Já existe uma cópia com este número para este livro"
        )
    
    db_copy = BookCopy(**copy.model_dump(), is_available=True)
    db.add(db_copy)
    db.commit()
    db.refresh(db_copy)
    return db_copy

@router.get("/copies/",tags=["Book Copies"], response_model=List[BookCopyResponse])
def list_book_copies(db: Session = Depends(get_db)):
    copies = db.query(BookCopy).all()
    return copies

@router.get("/copies/{copy_id}",tags=["Book Copies"], response_model=BookCopyResponse)
def get_book_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    return copy

@router.put("/copies/{copy_id}",tags=["Book Copies"], response_model=BookCopyResponse)
def update_book_copy(copy_id: int, copy: BookCopyUpdate, db: Session = Depends(get_db)):
    db_copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if db_copy is None:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    
    # Se estiver atualizando o número da cópia, verificar se já existe outra cópia com o mesmo número
    if copy.copy_number and copy.copy_number != db_copy.copy_number:
        copy_existente = db.query(BookCopy).filter(
            BookCopy.book_id == db_copy.book_id,
            BookCopy.copy_number == copy.copy_number
        ).first()
        if copy_existente:
            raise HTTPException(
                status_code=400, 
                detail="Já existe uma cópia com este número para este livro"
            )
    
    update_data = copy.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_copy, key, value)
    
    db.commit()
    db.refresh(db_copy)
    return db_copy

@router.delete("/copies/{copy_id}",tags=["Book Copies"])
def delete_book_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    
    # Verificar se a cópia está emprestada
    if not copy.is_available:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível deletar uma cópia que está emprestada"
        )
    
    db.delete(copy)
    db.commit()
    return {"message": "Cópia do livro deletada com sucesso"}

@router.get("/{book_id}/copies",tags=["Book Copies"], response_model=List[BookCopyResponse])
def list_copies_by_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    copies = db.query(BookCopy).filter(BookCopy.book_id == book_id).all()
    return copies

@router.get("/copies/available",tags=["Book Copies"], response_model=List[BookCopyResponse])
def list_available_copies(db: Session = Depends(get_db)):
    copies = db.query(BookCopy).filter(BookCopy.is_available == True).all()
    return copies

@router.get("/copies/unavailable",tags=["Book Copies"], response_model=List[BookCopyResponse])
def list_unavailable_copies(db: Session = Depends(get_db)):
    copies = db.query(BookCopy).filter(BookCopy.is_available == False).all()
    return copies

@router.get("/copies/condition/{condition}",tags=["Book Copies"], response_model=List[BookCopyResponse])
def list_copies_by_condition(condition: str, db: Session = Depends(get_db)):
    copies = db.query(BookCopy).filter(BookCopy.condition == condition).all()
    return copies

@router.get("/copies/location/{location}",tags=["Book Copies"], response_model=List[BookCopyResponse])
def list_copies_by_location(location: str, db: Session = Depends(get_db)):
    copies = db.query(BookCopy).filter(BookCopy.location.ilike(f"%{location}%")).all()
    return copies 
