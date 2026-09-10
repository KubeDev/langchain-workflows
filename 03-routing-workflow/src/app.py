from fastapi import FastAPI

from contratos import Resultado, Solicitacao
from workflow import executar_workflow

app = FastAPI(
    title="Routing de Solicitacoes DevOps",
    description="Direciona cada solicitacao para um modelo especializado.",
    version="0.1.0",
)


@app.post("/triagens")
def criar_triagem(solicitacao: Solicitacao) -> Resultado:
    return executar_workflow(solicitacao)
