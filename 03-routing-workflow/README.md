# Routing de solicitacoes DevOps

Exemplo didatico de routing com LangChain. Um modelo da OpenAI classifica uma solicitacao e `RunnableBranch` executa somente uma entre quatro tratativas previamente definidas.

O projeto nao usa LangGraph, agentes, ferramentas, memoria ou triagem deterministica.

```text
Solicitacao
    |
    v
OpenAI: classificar a rota
    |
    v
RunnableBranch
    +--> pipeline       -> Anthropic
    +--> infraestrutura -> OpenAI
    +--> release        -> Anthropic
    +--> fallback       -> aplicacao
```

## Onde esta cada parte

O exemplo segue a mesma separacao do projeto anterior:

```text
src/
├── app.py        # endpoint web
├── contratos.py  # entrada, decisao do roteador e resultado comum
└── workflow.py   # modelos, prompts, chains e routing
```

Dentro de `src/workflow.py`, o fluxo aparece nesta ordem:

1. modelo, system prompt e chain do roteador;
2. modelo, system prompt e chain de pipeline;
3. modelo, system prompt e chain de infraestrutura;
4. modelo, system prompt e chain de release;
5. funcoes que executam as tratativas;
6. `RunnableBranch`;
7. execucao passo a passo.

`src/app.py` fica pequeno: recebe `Solicitacao`, chama `executar_workflow()` e devolve `Resultado`.

## Modelos usados

| Papel | Provider | Modelo |
|---|---|---|
| Classificar a solicitacao | OpenAI | `gpt-5.6-luna` |
| Analisar falha de pipeline | Anthropic | `claude-sonnet-5` |
| Revisar infraestrutura como codigo | OpenAI | `gpt-5.6-sol` |
| Escrever comunicacao de release | Anthropic | `claude-haiku-4-5-20251001` |

O catalogo e uma escolha didatica. O exemplo nao compara qualidade, preco ou latencia dos modelos.

## RunnableSequence e RunnableBranch

O operador `|` cria uma sequencia de Runnables. Por exemplo:

```python
pipeline_chain = pipeline_prompt | pipeline_model | StrOutputParser()
```

Essa `RunnableSequence` sempre executa prompt, modelo e parser nessa ordem.

`RunnableBranch` resolve outro problema: escolher somente uma entre varias sequencias. Ele avalia as condicoes em ordem, executa o primeiro ramo verdadeiro e usa o ultimo Runnable como caminho padrao.

## Executar

Crie o arquivo de ambiente:

```bash
cp .env.example .env
```

Preencha:

```dotenv
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

Instale as dependencias:

```bash
uv sync
```

Inicie a API:

```bash
uv run fastapi dev src/app.py
```

Abra `http://127.0.0.1:8000/docs` e execute `POST /triagens` com os arquivos de `entradas/`.

Pelo terminal:

```bash
curl --fail-with-body \
  --request POST \
  --header 'Content-Type: application/json' \
  --data @entradas/falha-pipeline.json \
  http://127.0.0.1:8000/triagens
```

A resposta mostra a rota escolhida, o provider, o modelo e o texto produzido pela tratativa selecionada.

## Saidas de referencia

Estas saidas sao exemplos didaticos do caminho esperado, nao capturas das APIs. Elas permitem localizar a troca de ramo antes da execucao ao vivo, cujo texto e classificacao podem variar.

Falha de pipeline:

```json
{
  "rota": "pipeline",
  "provider": "anthropic",
  "modelo": "claude-sonnet-5",
  "resposta": "..."
}
```

Revisao de Terraform:

```json
{
  "rota": "infraestrutura",
  "provider": "openai",
  "modelo": "gpt-5.6-sol",
  "resposta": "..."
}
```

Solicitacao ambigua:

```json
{
  "rota": "fallback",
  "provider": "aplicacao",
  "modelo": "nenhum",
  "resposta": "A solicitacao precisa ser esclarecida ou dividida..."
}
```

## O que observar

- o roteador sempre usa o mesmo modelo e o mesmo system prompt;
- cada caminho possui seu proprio modelo e system prompt;
- apenas uma tratativa e executada por solicitacao;
- todas as tratativas devolvem as mesmas quatro chaves;
- uma rota valida ainda pode representar uma classificacao semanticamente incorreta;
- uma solicitacao ambigua pode seguir para `fallback`.

## Referencias

- [LangChain Core — RunnableBranch](https://reference.langchain.com/python/langchain-core/runnables/branch/RunnableBranch)
- [LangChain Core — RunnableSequence](https://reference.langchain.com/python/langchain-core/runnables/base/RunnableSequence)
- [LangChain — ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [LangChain — ChatAnthropic](https://docs.langchain.com/oss/python/integrations/chat/anthropic)
