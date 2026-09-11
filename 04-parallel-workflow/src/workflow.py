from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

from contratos import Analise, AnalisesParalelas, Consolidacao, Incidente, Resultado

load_dotenv()


# 1. Modelo, system prompt e chain para a perspectiva de pipeline

pipeline_model = ChatOpenAI(model="gpt-5.6-luna")

pipeline_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce analisa incidentes pela perspectiva do pipeline de entrega. "
            "Use somente os dados recebidos, separe evidencias de hipotese e "
            "devolva perspectiva='pipeline'.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

pipeline_chain = pipeline_prompt | pipeline_model.with_structured_output(Analise)


# 2. Modelo, system prompt e chain para a perspectiva de infraestrutura

infraestrutura_model = ChatOpenAI(model="gpt-5.6-luna")

infraestrutura_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce analisa incidentes pela perspectiva de infraestrutura. "
            "Considere capacidade, rede, computacao e dependencias gerenciadas. "
            "Use somente os dados recebidos, separe evidencias de hipotese e "
            "devolva perspectiva='infraestrutura'.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

infraestrutura_chain = (
    infraestrutura_prompt
    | infraestrutura_model.with_structured_output(Analise)
)


# 3. Modelo, system prompt e chain para a perspectiva de aplicacao

aplicacao_model = ChatOpenAI(model="gpt-5.6-luna")

aplicacao_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce analisa incidentes pela perspectiva da aplicacao. "
            "Considere comportamento em runtime, dependencias, latencia e erros. "
            "Use somente os dados recebidos, separe evidencias de hipotese e "
            "devolva perspectiva='aplicacao'.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

aplicacao_chain = aplicacao_prompt | aplicacao_model.with_structured_output(Analise)


# 4. Execucao paralela das tres perspectivas independentes

analises_paralelas = RunnableParallel(
    pipeline=pipeline_chain,
    infraestrutura=infraestrutura_chain,
    aplicacao=aplicacao_chain,
)


# 5. Modelo, system prompt e chain que consolidam os resultados

consolidacao_model = ChatOpenAI(model="gpt-5.6-luna")

consolidacao_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce consolida analises independentes de um incidente. Preserve "
            "divergencias entre os especialistas, nao transforme hipoteses em "
            "fatos e proponha apenas proximos passos de verificacao.",
        ),
        ("human", "Analises independentes:\n{analises}"),
    ]
)

consolidacao_chain = (
    consolidacao_prompt
    | consolidacao_model.with_structured_output(Consolidacao)
)


# 6. Workflow executado passo a passo


def executar_workflow(incidente: Incidente) -> Resultado:
    entrada = incidente.model_dump()

    resultados = analises_paralelas.invoke(entrada)
    analises = AnalisesParalelas.model_validate(resultados)

    consolidacao = consolidacao_chain.invoke(
        {"analises": analises.model_dump_json(indent=2)}
    )

    return Resultado(
        analises=analises,
        consolidacao=consolidacao,
    )
