from typing import Literal

from pydantic import BaseModel


class Solicitacao(BaseModel):
    titulo: str
    descricao: str


class Roteamento(BaseModel):
    destino: Literal["pipeline", "infraestrutura", "release", "fallback"]


class Resultado(BaseModel):
    rota: str
    provider: str
    modelo: str
    resposta: str
