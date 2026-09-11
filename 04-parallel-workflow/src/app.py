from fastapi import FastAPI

from contratos import Incidente, Resultado
from workflow import executar_workflow

app = FastAPI(
    title="Analise Paralela de Incidentes",
    description="Executa analises independentes e consolida os resultados.",
    version="0.1.0",
)


@app.post("/analises")
def criar_analise(incidente: Incidente) -> Resultado:
    return executar_workflow(incidente)
