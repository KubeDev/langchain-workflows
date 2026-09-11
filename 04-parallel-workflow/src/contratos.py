from typing import Literal

from pydantic import BaseModel


class Incidente(BaseModel):
    titulo: str
    descricao: str


class Analise(BaseModel):
    perspectiva: Literal["pipeline", "infraestrutura", "aplicacao"]
    evidencias: list[str]
    hipotese: str
    severidade: Literal["baixa", "media", "alta", "critica"]


class AnalisesParalelas(BaseModel):
    pipeline: Analise
    infraestrutura: Analise
    aplicacao: Analise


class Consolidacao(BaseModel):
    resumo: str
    convergencias: list[str]
    divergencias: list[str]
    proximos_passos: list[str]


class Resultado(BaseModel):
    analises: AnalisesParalelas
    consolidacao: Consolidacao
