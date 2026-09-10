import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from contratos import (
    AlertaEntrada,
    AnaliseIncidente,
    Evidencias,
    Hipotese,
    PlanoVerificacao,
)

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise SystemExit("Configure GOOGLE_API_KEY no arquivo .env antes de executar.")

model = init_chat_model("google_genai:gemini-3.8-flash")

prompt_evidencias = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce analisa alertas operacionais. Extraia somente fatos presentes "
            "na entrada. Nao formule causa, hipotese ou acao.",
        ),
        ("human", "Origem: {origem}\n\nAlerta:\n\n{alerta}"),
    ]
)

prompt_hipotese = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce formula uma unica hipotese operacional verificavel. Use somente "
            "as evidencias recebidas, diferencie fato de inferencia e registre "
            "o que ainda precisa ser confirmado.",
        ),
        ("human", "Evidencias validadas:\n\n{evidencias}"),
    ]
)

prompt_plano = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce cria um plano inicial e curto para verificar uma hipotese "
            "operacional. Inclua apenas acoes de leitura ou comparacao. "
            "Nao proponha correcao antes da verificacao.",
        ),
        (
            "human",
            "Evidencias validadas:\n\n{evidencias}\n\n"
            "Hipotese validada:\n\n{hipotese}",
        ),
    ]
)

modelo_evidencias = model.with_structured_output(
    Evidencias,
    method="json_schema",
)

modelo_hipotese = model.with_structured_output(
    Hipotese,
    method="json_schema",
)

modelo_plano = model.with_structured_output(
    PlanoVerificacao,
    method="json_schema",
)

chain_evidencias = prompt_evidencias | modelo_evidencias
chain_hipotese = prompt_hipotese | modelo_hipotese
chain_plano = prompt_plano | modelo_plano


def executar_workflow(entrada: AlertaEntrada) -> AnaliseIncidente:
    evidencias = chain_evidencias.invoke(
        {
            "origem": entrada.origem,
            "alerta": entrada.alerta,
        }
    )
    print(f"Evidencias: {type(evidencias).__name__}")

    evidencias_json = evidencias.model_dump_json()
    hipotese = chain_hipotese.invoke({"evidencias": evidencias_json})
    print(f"Hipotese: {type(hipotese).__name__}")

    hipotese_json = hipotese.model_dump_json()
    plano = chain_plano.invoke(
        {
            "evidencias": evidencias_json,
            "hipotese": hipotese_json,
        }
    )
    print(f"Plano: {type(plano).__name__}")

    return AnaliseIncidente(
        evidencias=evidencias,
        hipotese=hipotese,
        plano=plano,
    )
