# Analise paralela de incidentes

Exemplo didatico de execucoes independentes com LangChain. O mesmo incidente e enviado para tres analises especializadas, `RunnableParallel` executa os ramos concorrentemente e uma quarta chain consolida os resultados.

O projeto nao usa LangGraph, agentes, ferramentas, memoria, retry ou fallback.

```text
Incidente
    |
    v
RunnableParallel
    +--> pipeline       -> Analise
    +--> infraestrutura -> Analise
    +--> aplicacao      -> Analise
    |
    v
AnalisesParalelas
    |
    v
consolidacao_chain -> Consolidacao
```

## Onde esta cada parte

```text
src/
├── app.py        # endpoint web
├── contratos.py  # entrada, analises especializadas e resultado consolidado
└── workflow.py   # modelos, prompts, chains e paralelizacao
```

Dentro de `src/workflow.py`, o fluxo aparece nesta ordem:

1. modelo, system prompt e chain de pipeline;
2. modelo, system prompt e chain de infraestrutura;
3. modelo, system prompt e chain de aplicacao;
4. `RunnableParallel` com os tres ramos;
5. modelo, system prompt e chain de consolidacao;
6. execucao passo a passo.

`src/app.py` fica pequeno: recebe `Incidente`, chama `executar_workflow()` e devolve `Resultado`.

## Modelo usado

As quatro chamadas usam `gpt-5.6-luna`. Manter o mesmo modelo deixa a demonstracao concentrada na estrutura do workflow, e nao na comparacao entre modelos ou providers.

## RunnableParallel

As tres chains recebem o mesmo dicionario com `titulo` e `descricao`:

```python
analises_paralelas = RunnableParallel(
    pipeline=pipeline_chain,
    infraestrutura=infraestrutura_chain,
    aplicacao=aplicacao_chain,
)
```

Os ramos nao consomem o resultado uns dos outros. A chamada abaixo devolve um dicionario com as chaves `pipeline`, `infraestrutura` e `aplicacao`:

```python
resultados = analises_paralelas.invoke(entrada)
```

A consolidacao acontece somente depois que esse mapa esta completo. Ela e o ponto de fan-in do exemplo.

## Executar

Crie o arquivo de ambiente:

```bash
cp .env.example .env
```

Preencha:

```dotenv
OPENAI_API_KEY=...
```

Instale as dependencias:

```bash
uv sync
```

Inicie a API:

```bash
uv run fastapi dev src/app.py
```

Abra `http://127.0.0.1:8000/docs` e execute `POST /analises` com `entradas/incidente.json`.

Pelo terminal:

```bash
curl --fail-with-body \
  --request POST \
  --header 'Content-Type: application/json' \
  --data @entradas/incidente.json \
  http://127.0.0.1:8000/analises
```

## Saida de referencia

A estrutura abaixo e uma referencia didatica, nao uma captura da API. Textos, severidades e quantidade de itens podem variar entre execucoes.

```json
{
  "analises": {
    "pipeline": {
      "perspectiva": "pipeline",
      "evidencias": ["O deploy terminou sem falhas"],
      "hipotese": "A verificacao do pipeline nao cobriu o comportamento depois do deploy",
      "severidade": "alta"
    },
    "infraestrutura": {
      "perspectiva": "infraestrutura",
      "evidencias": ["Os pods aparecem como prontos", "O pool de conexoes esta perto do limite"],
      "hipotese": "A capacidade disponivel para conexoes pode estar contribuindo para a degradacao",
      "severidade": "alta"
    },
    "aplicacao": {
      "perspectiva": "aplicacao",
      "evidencias": ["A taxa de 503 subiu para 18%", "A latencia chegou a 1,9 s"],
      "hipotese": "A nova versao pode estar pressionando uma dependencia durante as requisicoes",
      "severidade": "critica"
    }
  },
  "consolidacao": {
    "resumo": "O incidente comecou depois do deploy e combina degradacao de latencia, erros 503 e pressao no pool de conexoes.",
    "convergencias": ["As perspectivas relacionam a degradacao ao periodo posterior ao deploy"],
    "divergencias": ["Os especialistas atribuem pesos diferentes ao pipeline, a capacidade e ao comportamento da aplicacao"],
    "proximos_passos": ["Comparar a versao atual com a anterior", "Verificar o uso e a espera por conexoes"]
  }
}
```

## O que observar

- os tres ramos recebem exatamente a mesma entrada;
- nenhuma analise depende da saida de outra;
- um unico `invoke()` dispara as tres chains;
- o resultado paralelo e um mapa nomeado;
- a consolidacao so executa depois que todos os ramos terminam;
- quatro chamadas de modelo sao feitas: tres analises e uma consolidacao;
- a concorrencia reduz o tempo de parede dos ramos, mas nao reduz a quantidade de chamadas.

## Limites intencionais

- se um ramo levantar erro, a invocacao paralela simples falha;
- nao ha retry, fallback ou preservacao de resultado parcial;
- structured output valida o formato, nao a qualidade semantica da analise;
- a consolidacao pode preservar divergencias, mas continua sendo probabilistica;
- tratamento de falha e confiabilidade ficam para o capitulo de middleware.

## Referencias

- [LangChain Core — RunnableParallel](https://reference.langchain.com/python/langchain-core/runnables/base/RunnableParallel)
- [LangChain Core — Runnable](https://reference.langchain.com/python/langchain-core/runnables/base/Runnable)
- [LangChain — ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai)
