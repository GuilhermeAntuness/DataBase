from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.cargo import Cargo
from app.models.pessoa import Funcionario
from database import get_db

router = APIRouter(prefix="/cargos")

class CargoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    salario_base: float
    nivel_hierarquico: int

class CargoCreate(CargoBase):
    pass

class CargoResponse(CargoBase):
    id: int

    class Config:
        from_attributes = True

class CargoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    salario_base: Optional[float] = None
    nivel_hierarquico: Optional[int] = None

@router.post("/", response_model=CargoResponse, status_code=201)
def criar_cargo(cargo: CargoCreate, db: Session = Depends(get_db)):
    # Verificar se já existe um cargo com o mesmo nome
    cargo_existente = db.query(Cargo).filter(Cargo.nome == cargo.nome).first()
    if cargo_existente:
        raise HTTPException(status_code=400, detail="Já existe um cargo com este nome")
    
    db_cargo = Cargo(**cargo.model_dump())
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

@router.get("/", response_model=List[CargoResponse])
def listar_cargos(db: Session = Depends(get_db)):
    cargos = db.query(Cargo).all()
    return cargos

@router.get("/{cargo_id}", response_model=CargoResponse)
def obter_cargo(cargo_id: int, db: Session = Depends(get_db)):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    return cargo

@router.put("/{cargo_id}", response_model=CargoResponse)
def atualizar_cargo(cargo_id: int, cargo: CargoUpdate, db: Session = Depends(get_db)):
    db_cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not db_cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Se estiver atualizando o nome, verificar se já existe outro cargo com o mesmo nome
    if cargo.nome and cargo.nome != db_cargo.nome:
        cargo_existente = db.query(Cargo).filter(Cargo.nome == cargo.nome).first()
        if cargo_existente:
            raise HTTPException(status_code=400, detail="Já existe um cargo com este nome")
    
    update_data = cargo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cargo, key, value)
    
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

@router.delete("/{cargo_id}")
def deletar_cargo(cargo_id: int, db: Session = Depends(get_db)):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Verificar se existem funcionários vinculados a este cargo
    funcionarios = db.query(Funcionario).filter(Funcionario.cargo_id == cargo_id).first()
    if funcionarios:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível deletar este cargo pois existem funcionários vinculados a ele"
        )
    
    db.delete(cargo)
    db.commit()
    return {"message": "Cargo deletado com sucesso"}

@router.get("/{cargo_id}/funcionarios", response_model=List[dict])
def listar_funcionarios_cargo(cargo_id: int, db: Session = Depends(get_db)):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    funcionarios = db.query(Funcionario).filter(Funcionario.cargo_id == cargo_id).all()
    return [
        {
            "id": f.id,
            "nome": f.nome,
            "cpf": f.cpf,
            "email": f.email,
            "data_contratacao": f.data_contratacao,
            "salario": f.salario,
            "ativo": f.ativo
        }
        for f in funcionarios
    ] 