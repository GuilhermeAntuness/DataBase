from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.pessoa import Pessoa, Cliente, Funcionario
from app.models.cargo import Cargo
from database import get_db

router = APIRouter(prefix="/pessoas",tags=['Pessoa'])

# Schemas para Pessoa
class PessoaBase(BaseModel):
    nome: str
    cpf: str
    data_nascimento: date
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None

class PessoaCreate(PessoaBase):
    pass

class PessoaResponse(PessoaBase):
    id: int
    tipo: str

    class Config:
        from_attributes = True

class PessoaUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None

# Schemas para Cliente
class ClienteBase(PessoaBase):
    data_cadastro: date
    status: str = 'ativo'

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    tipo: str

    class Config:
        from_attributes = True

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[str] = None

# Schemas para Funcionario
class FuncionarioBase(PessoaBase):
    cargo_id: int
    data_contratacao: date
    salario: float
    ativo: bool = True

class FuncionarioCreate(FuncionarioBase):
    pass

class FuncionarioResponse(FuncionarioBase):
    id: int
    tipo: str
    cargo_nome: Optional[str] = None

    class Config:
        from_attributes = True

class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cargo_id: Optional[int] = None
    salario: Optional[float] = None
    ativo: Optional[bool] = None

# Endpoints para Pessoas (geral)
@router.get("/", response_model=List[PessoaResponse])
def listar_pessoas(db: Session = Depends(get_db)):
    pessoas = db.query(Pessoa).all()
    return pessoas

@router.get("/{pessoa_id}", response_model=PessoaResponse)
def obter_pessoa(pessoa_id: int, db: Session = Depends(get_db)):
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return pessoa

@router.put("/{pessoa_id}", response_model=PessoaResponse)
def atualizar_pessoa(pessoa_id: int, pessoa: PessoaUpdate, db: Session = Depends(get_db)):
    db_pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not db_pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    update_data = pessoa.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pessoa, key, value)
    
    db.commit()
    db.refresh(db_pessoa)
    return db_pessoa

@router.delete("/{pessoa_id}")
def deletar_pessoa(pessoa_id: int, db: Session = Depends(get_db)):
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    db.delete(pessoa)
    db.commit()
    return {"message": "Pessoa deletada com sucesso"}

# Endpoints para Clientes
@router.post("/clientes", response_model=ClienteResponse, status_code=201)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Verificar se já existe uma pessoa com o mesmo CPF
    pessoa_existente = db.query(Pessoa).filter(Pessoa.cpf == cliente.cpf).first()
    if pessoa_existente:
        raise HTTPException(status_code=400, detail="Já existe uma pessoa com este CPF")
    
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/clientes", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return clientes

@router.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/clientes/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(cliente_id: int, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    update_data = cliente.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.delete("/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente deletado com sucesso"}

@router.get("/clientes/status/{status}", response_model=List[ClienteResponse])
def listar_clientes_por_status(status: str, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).filter(Cliente.status == status).all()
    return clientes

# Endpoints para Funcionários
@router.post("/funcionarios", response_model=FuncionarioResponse, status_code=201)
def criar_funcionario(funcionario: FuncionarioCreate, db: Session = Depends(get_db)):
    # Verificar se já existe uma pessoa com o mesmo CPF
    pessoa_existente = db.query(Pessoa).filter(Pessoa.cpf == funcionario.cpf).first()
    if pessoa_existente:
        raise HTTPException(status_code=400, detail="Já existe uma pessoa com este CPF")
    
    # Verificar se o cargo existe
    cargo = db.query(Cargo).filter(Cargo.id == funcionario.cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    db_funcionario = Funcionario(**funcionario.model_dump())
    db.add(db_funcionario)
    db.commit()
    db.refresh(db_funcionario)
    
    # Adicionar nome do cargo na resposta
    response_data = FuncionarioResponse.model_validate(db_funcionario)
    response_data.cargo_nome = cargo.nome
    return response_data

@router.get("/funcionarios", response_model=List[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).all()
    result = []
    for func in funcionarios:
        response_data = FuncionarioResponse.model_validate(func)
        if func.cargo:
            response_data.cargo_nome = func.cargo.nome
        result.append(response_data)
    return result

@router.get("/funcionarios/{funcionario_id}", response_model=FuncionarioResponse)
def obter_funcionario(funcionario_id: int, db: Session = Depends(get_db)):
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    response_data = FuncionarioResponse.model_validate(funcionario)
    if funcionario.cargo:
        response_data.cargo_nome = funcionario.cargo.nome
    return response_data

@router.put("/funcionarios/{funcionario_id}", response_model=FuncionarioResponse)
def atualizar_funcionario(funcionario_id: int, funcionario: FuncionarioUpdate, db: Session = Depends(get_db)):
    db_funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not db_funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    # Se estiver atualizando o cargo, verificar se existe
    if funcionario.cargo_id:
        cargo = db.query(Cargo).filter(Cargo.id == funcionario.cargo_id).first()
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    update_data = funcionario.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_funcionario, key, value)
    
    db.commit()
    db.refresh(db_funcionario)
    
    response_data = FuncionarioResponse.model_validate(db_funcionario)
    if db_funcionario.cargo:
        response_data.cargo_nome = db_funcionario.cargo.nome
    return response_data

@router.delete("/funcionarios/{funcionario_id}")
def deletar_funcionario(funcionario_id: int, db: Session = Depends(get_db)):
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    db.delete(funcionario)
    db.commit()
    return {"message": "Funcionário deletado com sucesso"}

@router.get("/funcionarios/cargo/{cargo_id}", response_model=List[FuncionarioResponse])
def listar_funcionarios_por_cargo(cargo_id: int, db: Session = Depends(get_db)):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    funcionarios = db.query(Funcionario).filter(Funcionario.cargo_id == cargo_id).all()
    result = []
    for func in funcionarios:
        response_data = FuncionarioResponse.model_validate(func)
        response_data.cargo_nome = cargo.nome
        result.append(response_data)
    return result

@router.get("/funcionarios/ativos", response_model=List[FuncionarioResponse])
def listar_funcionarios_ativos(db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).filter(Funcionario.ativo == True).all()
    result = []
    for func in funcionarios:
        response_data = FuncionarioResponse.model_validate(func)
        if func.cargo:
            response_data.cargo_nome = func.cargo.nome
        result.append(response_data)
    return result

# Endpoint para buscar pessoa por CPF
@router.get("/cpf/{cpf}", response_model=PessoaResponse)
def buscar_pessoa_por_cpf(cpf: str, db: Session = Depends(get_db)):
    pessoa = db.query(Pessoa).filter(Pessoa.cpf == cpf).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return pessoa 