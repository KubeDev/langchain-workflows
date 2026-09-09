import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise SystemExit("Configure GOOGLE_API_KEY no arquivo .env antes de executar.")

model = init_chat_model("google_genai:gemini-3.8-flash")


# Cada etapa e uma chain: prompt -> modelo -> parser.
# StrOutputParser converte o AIMessage em str para a proxima etapa.

prompt_evidencias = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce analisa alertas operacionais. Extraia somente evidencias presentes "
            "na entrada, sem formular causa ou acao.",
        ),
        ("human", "Alerta:\n\n{alerta}"),
    ]
)

prompt_hipotese = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce formula uma unica hipotese operacional a partir das evidencias "
            "recebidas. Diferencie fato de inferencia.",
        ),
        ("human", "Evidencias:\n\n{evidencias}"),
    ]
)

prompt_plano = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce cria um plano inicial e curto para verificar uma hipotese "
            "operacional. Nao proponha correcao antes da verificacao.",
        ),
        ("human", "Hipotese:\n\n{hipotese}"),
    ]
)


alerta = Path("alerta.txt").read_text(encoding="utf-8")

chain_evidencias = prompt_evidencias | model | StrOutputParser()
chain_hipotese = prompt_hipotese | model | StrOutputParser()
chain_plano = prompt_plano | model | StrOutputParser()

evidencias = chain_evidencias.invoke({"alerta": alerta})
print(f"EVIDENCIAS: \n{evidencias}")
print("\n\n------------------------------------------------------------\n\n")

hipotese = chain_hipotese.invoke({"evidencias": evidencias})
print(f"HIPOTESE: \n{hipotese}")
print("\n\n------------------------------------------------------------\n\n")

plano = chain_plano.invoke({"hipotese": hipotese})
print(f"PLANO: \n{plano}")
