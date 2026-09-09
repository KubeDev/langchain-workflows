# Workflow sequencial com LangChain

Exemplo didatico de prompt chaining aplicado a um alerta operacional. O projeto comeca com as chains executadas separadamente, deixando as strings intermediarias visiveis. Durante a aula, esse bloco e substituido por uma unica `RunnableSequence`.

## O problema

Um alerta bruto precisa virar um plano inicial de verificacao. Em vez de pedir tudo em uma chamada, o trabalho e decomposto em tres transformacoes dependentes:

```text
alerta -> evidencias -> hipotese -> plano de verificacao
```

A trajetoria e fixa. O modelo nao escolhe etapas, nao usa ferramentas e nao controla o fluxo.

## Anatomia das chains

Cada etapa combina tres Runnables:

```python
chain_evidencias = prompt_evidencias | model | StrOutputParser()
```

- `ChatPromptTemplate` transforma valores em mensagens.
- O modelo transforma mensagens em `AIMessage`.
- `StrOutputParser` extrai o conteudo como `str`.

`StrOutputParser` e apenas o parser mais simples. LangChain tambem fornece parsers para JSON, Pydantic, listas e XML. Quando o modelo oferece structured output nativo, a documentacao recomenda considera-lo antes de usar um parser estrutural. Esse criterio e assunto do exemplo seguinte; aqui todas as passagens usam texto.

## Duas formas de executar

### Etapa por etapa

```python
evidencias = chain_evidencias.invoke({"alerta": alerta})
hipotese = chain_hipotese.invoke({"evidencias": evidencias})
plano = chain_plano.invoke({"hipotese": hipotese})
```

Essa forma deixa cada resultado intermediario visivel e facilita observar a passagem de dados.

### Sequencia completa

Depois de executar e compreender a primeira versao, substitua o bloco final de `src/app.py` por:

```python
workflow = chain_evidencias | chain_hipotese | chain_plano

inicio = time.perf_counter()
plano = workflow.invoke({"alerta": alerta})
duracao = time.perf_counter() - inicio
print(f"\n{'=' * 72}\nPLANO FINAL ({duracao:.1f}s)\n{'=' * 72}")
print(plano)
```

`prompt_hipotese` e `prompt_plano` possuem uma unica variavel. Por isso, cada template aceita diretamente a string produzida pela chain anterior. A composicao completa recebe uma entrada e devolve somente a saida final.

## Como executar

```bash
cp .env.example .env
uv sync
```

Preencha `GOOGLE_API_KEY` no `.env` e execute:

```bash
uv run src/app.py
```

Execute novamente o mesmo comando depois de substituir o bloco pela sequencia completa. As respostas podem variar entre execucoes. O que permanece igual e a ordem das transformacoes.

## O que este exemplo nao faz

- saida estruturada ou validacao de contrato;
- routing;
- paralelizacao;
- ferramentas;
- memoria;
- LangGraph;
- agentes.

Cada ausencia preserva um unico objetivo: enxergar como a saida de uma chamada se torna a entrada da seguinte.

## Referencias

- [RunnableSequence](https://reference.langchain.com/python/langchain-core/runnables/base/RunnableSequence)
- [ChatPromptTemplate](https://reference.langchain.com/python/langchain-core/prompts/chat/ChatPromptTemplate)
- [StrOutputParser](https://reference.langchain.com/python/langchain-core/output_parsers/string/StrOutputParser)
- [Output parsers](https://reference.langchain.com/python/langchain-core/output_parsers)
