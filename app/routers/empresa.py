from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.models.empresa import Empresa
from database import get_db

router = APIRouter(prefix="/empresas")

class CompanyResponse(BaseModel):
    id: int
    cnpj: str
    razao_social: str
    email_contato: str

    class Config:
        from_attributes = True

class CompanyCreate(BaseModel):
    cnpj: str
    razao_social: str
    email_contato: str

class CompanyUpdate(BaseModel):
    cnpj: str | None = None
    razao_social: str | None = None
    email_contato: str | None = None

@router.get("/", response_model=List[CompanyResponse])
def listar_empresas(db: Session = Depends(get_db)):
    empresas = db.query(Empresa).all()
    return empresas

@router.post("/", response_model=CompanyResponse, status_code=201)
def criar_empresa(empresa: CompanyCreate, db: Session = Depends(get_db)):
    db_empresa = Empresa(
        cnpj=empresa.cnpj,
        razao_social=empresa.razao_social,
        email_contato=empresa.email_contato
    )
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

@router.get("/{empresa_id}", response_model=CompanyResponse)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

@router.put("/{empresa_id}", response_model=CompanyResponse)
def atualizar_empresa(empresa_id: int, empresa: CompanyUpdate, db: Session = Depends(get_db)):
    db_empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    update_data = empresa.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_empresa, key, value)
    
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

@router.delete("/{empresa_id}", status_code=204)
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    db.delete(empresa)
    db.commit()
    return None
