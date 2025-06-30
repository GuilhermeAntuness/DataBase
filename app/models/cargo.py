from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base


class Cargo(Base):
    __tablename__ = "cargo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(64), nullable=False, unique=True)
    descricao = Column(String(256), nullable=True)
    salario_base = Column(Float, nullable=False)
    nivel_hierarquico = Column(Integer, nullable=False)
    
    # Relationship with Funcionario
    funcionarios = relationship("Funcionario", back_populates="cargo") 