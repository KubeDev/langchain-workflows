from typing import Literal

from pydantic import BaseModel, Field


class AlertaEntrada(BaseModel):
    alerta: str = Field(
        min_length=1,
        description="Conteudo bruto do alerta operacional",
    )
    origem: str = Field(
        default="monitoramento",
        description="Sistema que enviou o alerta",
    )


class Evidencia(BaseModel):
    categoria: Literal["sintoma", "mudanca", "contexto"] = Field(
        description="Papel da evidencia na analise do incidente",
    )
    descricao: str = Field(
        description="Fato observado diretamente no alerta",
    )


class Evidencias(BaseModel):
    servico: str = Field(
        description="Servico afetado pelo alerta",
    )
    itens: list[Evidencia] = Field(
        min_length=1,
        description="Evidencias extraidas sem formular causa ou acao",
    )
    mudanca_recente: str | None = Field(
        default=None,
        description="Mudanca recente relacionada no tempo, quando informada",
    )


class Hipotese(BaseModel):
    descricao: str = Field(
        description="Uma unica hipotese operacional a ser verificada",
    )
    evidencias_relacionadas: list[str] = Field(
        min_length=1,
        description="Evidencias que sustentam a hipotese",
    )
    incertezas: list[str] = Field(
        default_factory=list,
        description="Informacoes que ainda faltam para confirmar a hipotese",
    )


class PassoVerificacao(BaseModel):
    ordem: int = Field(
        ge=1,
        description="Posicao do passo no plano de verificacao",
    )
    acao: str = Field(
        description="Acao de leitura ou comparacao a executar",
    )
    evidencia_esperada: str = Field(
        description="Resultado observavel usado para avaliar a hipotese",
    )


class PlanoVerificacao(BaseModel):
    objetivo: str = Field(
        description="O que o plano pretende confirmar ou descartar",
    )
    passos: list[PassoVerificacao] = Field(
        min_length=1,
        description="Sequencia curta de verificacoes sem acao corretiva",
    )
    criterio_encerramento: str = Field(
        description="Condicao que encerra a verificacao da hipotese",
    )


class AnaliseIncidente(BaseModel):
    evidencias: Evidencias
    hipotese: Hipotese
    plano: PlanoVerificacao
