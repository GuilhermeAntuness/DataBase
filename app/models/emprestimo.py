from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Emprestimo(Base):
    __tablename__ = "emprestimo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    livro_copia_id = Column(Integer, ForeignKey("book_copy.id"), nullable=False)
    data_retirada = Column(DateTime, nullable=False, default=datetime.now)
    data_devolucao_prevista = Column(DateTime, nullable=False)
    data_devolucao_real = Column(DateTime, nullable=True)
    valor_multa = Column(Float, nullable=True, default=0.0)
    status = Column(String(20), nullable=False, default='ativo')  # ativo, devolvido, atrasado
    
    # Relationships
    cliente = relationship("Cliente", backref="emprestimos")
    livro_copia = relationship("BookCopy", backref="emprestimos") 