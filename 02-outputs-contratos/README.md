# Outputs e contratos do workflow

Exemplo didatico que recebe um alerta por uma API FastAPI, processa o incidente em tres chamadas sequenciais com LangChain e devolve uma resposta JSON estruturada.

```text
JSON de entrada
  -> AlertaEntrada
    -> Evidencias
      -> Hipotese
        -> PlanoVerificacao
          -> AnaliseIncidente
            -> JSON de saida
```

O caso operacional e o mesmo da aula anterior: um aumento de erros no `checkout-api` depois de um deploy. A mudanca esta no contrato. Em vez de transportar strings livres, cada chamada devolve uma instancia Pydantic validada.

## Estrutura

```text
.
├── entrada.json
└── src
    ├── app.py
    ├── contratos.py
    └── workflow.py
```

- `src/contratos.py`: modelos da entrada da API, dos resultados intermediarios e da resposta.
- `src/workflow.py`: prompts, structured outputs e execucao sequencial.
- `src/app.py`: endpoint que conecta o contrato HTTP ao workflow.
- `entrada.json`: payload pronto para executar a demonstracao.

## Contratos nas fronteiras

O endpoint recebe `AlertaEntrada` e devolve `AnaliseIncidente`:

```python
@app.post("/analises")
def analisar_incidente(entrada: AlertaEntrada) -> AnaliseIncidente:
    return executar_workflow(entrada)
```

FastAPI usa esses tipos para validar e serializar os dados e para gerar os schemas OpenAPI exibidos na documentacao interativa.

Dentro do workflow, `with_structured_output()` liga cada chamada a um modelo Pydantic:

```python
modelo_evidencias = model.with_structured_output(
    Evidencias,
    method="json_schema",
)
chain_evidencias = prompt_evidencias | modelo_evidencias
```

O retorno e uma instancia de `Evidencias`, nao uma string. Antes de alimentar o prompt seguinte, o objeto e serializado com `model_dump_json()`.

## Como executar

Crie o arquivo de ambiente e informe sua chave da Gemini Developer API:

```bash
cp .env.example .env
```

Instale as dependencias:

```bash
uv sync
```

Inicie a API:

```bash
uv run fastapi dev src/app.py
```

Abra `http://127.0.0.1:8000/docs`, expanda `POST /analises`, selecione **Try it out** e use o conteudo de `entrada.json`.

Como alternativa, mantenha a API em execucao e envie o arquivo pelo terminal:

```bash
curl --fail-with-body \
  --request POST \
  --header 'Content-Type: application/json' \
  --data @entrada.json \
  http://127.0.0.1:8000/analises
```

O terminal da API mostra o tipo produzido por cada etapa:

```text
Evidencias: Evidencias
Hipotese: Hipotese
Plano: PlanoVerificacao
```

A resposta HTTP agrega os tres objetos. O texto pode variar entre execucoes, mas os campos, tipos e estruturas aninhadas continuam definidos pelos contratos.

## O que o contrato garante

- formato conhecido na entrada e na saida da API;
- campos e tipos declarados no codigo;
- resultados intermediarios validados como modelos Pydantic;
- JSON Schema gerado para a documentacao OpenAPI;
- serializacao previsivel dos objetos para JSON.

O contrato nao garante que a hipotese esteja correta. Estrutura valida e qualidade do conteudo sao problemas diferentes.

## O que este exemplo nao faz

- retry ou fallback para falhas do modelo;
- tratamento customizado de erros HTTP;
- autenticacao ou autorizacao da API;
- routing ou paralelizacao;
- ferramentas, memoria ou agentes;
- avaliacao da qualidade da analise.

Cada ausencia preserva o objetivo da aula: observar contratos na entrada, entre as etapas e na saida do workflow.

## Referencias

- [Pydantic Validation](https://pydantic.dev/docs/validation/latest/get-started/)
- [LangChain — Models, structured output](https://docs.langchain.com/oss/python/langchain/models#structured-output)
- [LangChain Google GenAI — `with_structured_output`](https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output)
- [FastAPI — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
