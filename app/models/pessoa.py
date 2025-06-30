from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class Pessoa(Base):
    __tablename__ = "pessoa"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(128), nullable=False)
    cpf = Column(String(11), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(64), nullable=True)
    telefone = Column(String(16), nullable=True)
    endereco = Column(String(256), nullable=True)
    
    # Discriminator column for inheritance
    tipo = Column(String(20), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'pessoa',
        'polymorphic_on': tipo
    }


class Cliente(Pessoa):
    __tablename__ = "cliente"

    id = Column(Integer, ForeignKey('pessoa.id'), primary_key=True)
    data_cadastro = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default='ativo')
    
    __mapper_args__ = {
        'polymorphic_identity': 'cliente',
    }


class Funcionario(Pessoa):
    __tablename__ = "funcionario"

    id = Column(Integer, ForeignKey('pessoa.id'), primary_key=True)
    cargo_id = Column(Integer, ForeignKey('cargo.id'), nullable=False)
    data_contratacao = Column(Date, nullable=False)
    salario = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True)
    
    # Relationship with Cargo
    cargo = relationship("Cargo", back_populates="funcionarios")
    
    __mapper_args__ = {
        'polymorphic_identity': 'funcionario',
    } 