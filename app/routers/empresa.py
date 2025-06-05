from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/empresas")

class CompanyResponse(BaseModel):
    id: int
    cnpj: str
    razao_social: str
    email_contato: str


@router.get("/", response_model=List[CompanyResponse])
def listar_empresas():
    
    return [CompanyResponse(
            id= 1,
            cnpj= 1234,
            razao_social = "Empresa teste ltda",
            email_contato = "contato@teste.com",
        )]
