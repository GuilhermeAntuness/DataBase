from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.emprestimo import Emprestimo
from app.models.book import BookCopy
from app.models.pessoa import Cliente
from database import get_db

router = APIRouter(prefix="/emprestimos",tags=['Emprestimo'])

class EmprestimoBase(BaseModel):
    cliente_id: int
    livro_copia_id: int
    data_devolucao_prevista: datetime

class EmprestimoCreate(EmprestimoBase):
    pass

class EmprestimoResponse(EmprestimoBase):
    id: int
    data_retirada: datetime
    data_devolucao_real: Optional[datetime] = None
    valor_multa: float
    status: str

    class Config:
        from_attributes = True

class EmprestimoUpdate(BaseModel):
    data_devolucao_real: Optional[datetime] = None
    valor_multa: Optional[float] = None
    status: Optional[str] = None

@router.post("/", response_model=EmprestimoResponse, status_code=201)
def criar_emprestimo(emprestimo: EmprestimoCreate, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == emprestimo.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar se a cópia do livro existe e está disponível
    livro_copia = db.query(BookCopy).filter(BookCopy.id == emprestimo.livro_copia_id).first()
    if not livro_copia:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    if not livro_copia.is_available:
        raise HTTPException(status_code=400, detail="Cópia do livro não está disponível")
    
    # Criar o empréstimo
    db_emprestimo = Emprestimo(
        cliente_id=emprestimo.cliente_id,
        livro_copia_id=emprestimo.livro_copia_id,
        data_retirada=datetime.now(),
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        status='ativo'
    )
    
    # Atualizar disponibilidade do livro
    livro_copia.is_available = False
    
    db.add(db_emprestimo)
    db.commit()
    db.refresh(db_emprestimo)
    return db_emprestimo

@router.get("/", response_model=List[EmprestimoResponse])
def listar_emprestimos(db: Session = Depends(get_db)):
    emprestimos = db.query(Emprestimo).all()
    return emprestimos

@router.get("/{emprestimo_id}", response_model=EmprestimoResponse)
def obter_emprestimo(emprestimo_id: int, db: Session = Depends(get_db)):
    emprestimo = db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    return emprestimo

@router.put("/{emprestimo_id}/devolver", response_model=EmprestimoResponse)
def devolver_livro(emprestimo_id: int, db: Session = Depends(get_db)):
    emprestimo = db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    if emprestimo.status != 'ativo':
        raise HTTPException(status_code=400, detail="Este empréstimo já foi devolvido")
    
    # Calcular multa se houver atraso
    data_atual = datetime.now()
    valor_multa = 0.0
    if data_atual > emprestimo.data_devolucao_prevista:
        dias_atraso = (data_atual - emprestimo.data_devolucao_prevista).days
        valor_multa = dias_atraso * 2.0  # R$ 2,00 por dia de atraso
    
    # Atualizar empréstimo
    emprestimo.data_devolucao_real = data_atual
    emprestimo.valor_multa = valor_multa
    emprestimo.status = 'devolvido'
    
    # Atualizar disponibilidade do livro
    livro_copia = db.query(BookCopy).filter(BookCopy.id == emprestimo.livro_copia_id).first()
    livro_copia.is_available = True
    
    db.commit()
    db.refresh(emprestimo)
    return emprestimo

@router.get("/cliente/{cliente_id}", response_model=List[EmprestimoResponse])
def listar_emprestimos_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    emprestimos = db.query(Emprestimo).filter(Emprestimo.cliente_id == cliente_id).all()
    return emprestimos

@router.get("/livro/{livro_copia_id}", response_model=List[EmprestimoResponse])
def listar_emprestimos_livro(livro_copia_id: int, db: Session = Depends(get_db)):
    livro_copia = db.query(BookCopy).filter(BookCopy.id == livro_copia_id).first()
    if not livro_copia:
        raise HTTPException(status_code=404, detail="Cópia do livro não encontrada")
    
    emprestimos = db.query(Emprestimo).filter(Emprestimo.livro_copia_id == livro_copia_id).all()
    return emprestimos 