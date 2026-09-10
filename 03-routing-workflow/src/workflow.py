from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI

from contratos import Resultado, Roteamento, Solicitacao

load_dotenv()


# 1. Modelo, system prompt e chain que classificam a solicitacao

router_model = ChatOpenAI(model="gpt-5.6-luna")

router_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Classifique a solicitacao em exatamente uma categoria: "
            "pipeline para falha em pipeline ou deploy; infraestrutura para revisao "
            "de Terraform, Kubernetes ou outra infraestrutura como codigo; release "
            "para comunicado ou release notes; fallback quando houver mais de uma "
            "intencao principal ou quando nenhuma categoria servir.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

router_chain = router_prompt | router_model.with_structured_output(Roteamento)


# 2. Modelo, system prompt e chain para falhas de pipeline

pipeline_model = ChatAnthropic(model="claude-sonnet-5")

pipeline_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce analisa falhas em pipelines de entrega. Resuma o estagio que "
            "falhou, separe evidencias de hipoteses e proponha verificacoes de "
            "leitura antes de qualquer correcao.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

pipeline_chain = pipeline_prompt | pipeline_model | StrOutputParser()


# 3. Modelo, system prompt e chain para revisao de infraestrutura

infraestrutura_model = ChatOpenAI(model="gpt-5.6-sol")

infraestrutura_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce revisa infraestrutura como codigo. Identifique o recurso "
            "alterado, aponte riscos verificaveis e produza observacoes objetivas "
            "para a revisao do pull request. Nao aplique a mudanca.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

infraestrutura_chain = (
    infraestrutura_prompt | infraestrutura_model | StrOutputParser()
)


# 4. Modelo, system prompt e chain para comunicacao de release

release_model = ChatAnthropic(model="claude-haiku-4-5-20251001")

release_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce escreve comunicacoes curtas de release. Separe mudancas e "
            "impacto operacional sem inventar funcionalidades que nao aparecem "
            "na solicitacao.",
        ),
        ("human", "Titulo: {titulo}\n\nDescricao:\n{descricao}"),
    ]
)

release_chain = release_prompt | release_model | StrOutputParser()


# 5. Tratativas executadas por cada caminho


def tratar_pipeline(entrada: dict) -> Resultado:
    resposta = pipeline_chain.invoke(entrada)
    return Resultado(
        rota="pipeline",
        provider="anthropic",
        modelo="claude-sonnet-5",
        resposta=resposta,
    )


def tratar_infraestrutura(entrada: dict) -> Resultado:
    resposta = infraestrutura_chain.invoke(entrada)
    return Resultado(
        rota="infraestrutura",
        provider="openai",
        modelo="gpt-5.6-sol",
        resposta=resposta,
    )


def tratar_release(entrada: dict) -> Resultado:
    resposta = release_chain.invoke(entrada)
    return Resultado(
        rota="release",
        provider="anthropic",
        modelo="claude-haiku-4-5-20251001",
        resposta=resposta,
    )


def tratar_fallback(entrada: dict) -> Resultado:
    return Resultado(
        rota="fallback",
        provider="aplicacao",
        modelo="nenhum",
        resposta=(
            "A solicitacao precisa ser esclarecida ou dividida antes de seguir "
            "para uma tratativa especializada."
        ),
    )


# 6. RunnableBranch que escolhe somente uma tratativa

branches = RunnableBranch(
    (
        lambda entrada: entrada["rota"] == "pipeline",
        RunnableLambda(tratar_pipeline),
    ),
    (
        lambda entrada: entrada["rota"] == "infraestrutura",
        RunnableLambda(tratar_infraestrutura),
    ),
    (
        lambda entrada: entrada["rota"] == "release",
        RunnableLambda(tratar_release),
    ),
    RunnableLambda(tratar_fallback),
)


# 7. Workflow executado passo a passo


def executar_workflow(solicitacao: Solicitacao) -> Resultado:
    entrada = solicitacao.model_dump()

    decisao = router_chain.invoke(entrada)

    entrada_com_rota = {
        **entrada,
        "rota": decisao.destino,
    }

    resultado = branches.invoke(entrada_com_rota)
    return resultado
