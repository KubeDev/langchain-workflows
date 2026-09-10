from fastapi import FastAPI

from contratos import AlertaEntrada, AnaliseIncidente
from workflow import executar_workflow

app = FastAPI(
    title="Analise de Incidentes",
    description="Workflow LangChain com contratos Pydantic na entrada e na saida.",
    version="0.1.0",
)


@app.post(
    "/analises",
    summary="Analisa um alerta operacional",
)
def analisar_incidente(entrada: AlertaEntrada) -> AnaliseIncidente:
    return executar_workflow(entrada)
