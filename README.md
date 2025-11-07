
# Aegis: Implementando o Framework DAWN

[](https://opensource.org/licenses/MIT)
[](https://www.python.org/)
[](https://fastapi.tiangolo.com/)

O Aegis é a implementação de referência do **DAWN (Distributed Agent Workflow Network)**, um framework arquitetônico projetado para permitir a interoperabilidade universal, descoberta e colaboração entre agentes de Inteligência Artificial heterogêneos.

## 1\. O Problema: Silos de IA

O cenário atual de IA é fragmentado. Agentes autônomos operam em ecossistemas isolados (como LangChain, crewAI, etc.), incapazes de colaborar com agentes externos. Isso leva à redundância de desenvolvimento e limita a complexidade dos problemas que podem ser resolvidos. O DAWN é proposto para quebrar esses silos, criando um padrão de comunicação para um ecossistema de IA verdadeiramente colaborativo.

## 2\. A Solução: Framework DAWN

O DAWN propõe um modelo de orquestração de cima para baixo, centrado em dois componentes principais, para criar um mercado global e meritocrático de capacidades de IA.

### Arquitetura Principal

A arquitetura do DAWN é composta por três pilares:

1.  **Principal Agent (Agente Principal):** O orquestrador central. Ele recebe solicitações do usuário, as decompõe em tarefas, planeja a execução e gerencia o contexto.
2.  **Gateway Agent (Agente de Gateway):** O registro de descoberta de serviços. Atua como um "catálogo inteligente" onde Agentes de Recurso (ferramentas, outros agentes) se registram e são descobertos com base em suas capacidades e métricas de desempenho (QoS).
3.  **Resource Agent (Agente de Recurso):** Qualquer agente ou ferramenta especializada (ex: uma calculadora, um agente de busca na web, um modelo de IA especializado) que oferece uma capacidade específica.

## 3\. Componentes Core do Aegis

Esta implementação no Aegis é dividida nos seguintes componentes principais, refletindo o blueprint do DAWN.

### 3.1. Principal Agent (`Aegis/core/principal_agent`)

Atua como o cérebro central da orquestração.

**Design Rationale:**

  * **Modos de Operação Flexíveis:** Suporta modos `NO_LLM`, `ASSISTED` (Copilot), `AGENT` e `HYBRID`, permitindo alternar entre fluxos de trabalho determinísticos e autônomos.
  * **Gerenciamento de Contexto:** Mantém um contexto hierárquico (`conversation_history`, `user_preferences`, `task_history`, `memory_bank`) para personalização e continuidade em tarefas complexas.
  * **Estratégias de Raciocínio:** Projetado para implementar múltiplos "motores de raciocínio" (ex: ReAct, ReWOO, ToT) para decomposição de tarefas.
  * **Cache de Recursos Locais:** Mantém um cache local de recursos para reduzir a sobrecarga de rede em consultas frequentes ao Gateway.

**Schema (`principalAgent.py`):**

  * `mode: OperationalMode`
  * `gateway_agents: List[GatewayAgent]`
  * `local_resources: Dict[str, Resource]`
  * `task_queue: List[Task]`
  * `execution_history: List[Dict]`
  * `context: Dict`
  * `reasoning_strategies: Dict`

### 3.2. Gateway Agent (`Aegis/core/gateway_agent`)

Gerencia o registro, validação e descoberta inteligente de todos os recursos disponíveis na rede.

**Design Rationale:**

  * **Registro de Índice Duplo:** Utiliza um `registry` (para busca O(1) por ID) e um `capability_index` (para descoberta O(1) por capacidade), essencial para alta performance.
  * **Rastreamento de Desempenho (QoS):** Cada recurso registrado tem suas próprias métricas de desempenho (`performance_metrics`, `success_rate`, `avg_response_time`). Isso permite que o Gateway atue como um selecionador inteligente, ranqueando recursos não apenas pela capacidade, mas pela performance histórica.
  * **Validação de Recursos:** Inclui `test_results` e `is_active`, permitindo que recursos com falha sejam graciosamente desativados sem serem removidos, garantindo a robustez do sistema.

**Schema (`gatewayAgent.py` e `gatewayAgent_shcemas.py`):**

  * `registry: Dict[str, RegisteredResource]`
  * `capability_index: Dict[str, List[str]]`
  * `security_filters: List[Callable]`
  * `gateway_metrics: Dict`
  * `RegisteredResource` (Schema):
      * `id: str`
      * `capabilities: List[str]`
      * `endpoint: str`
      * `api_shcema: Dict[str,Any]`
      * `manifest: Dict[str,Any]`
      * `performance_metrics: Dict[str, float]`
      * `is_active: bool`

## 4\. Stack de Tecnologia (MVP)

A metodologia para o MVP deste projeto utilizará as seguintes tecnologias:

  * **Backend:** Python (FastAPI) e Node.js para os serviços dos agentes.
  * **Protocolos:** A2A (Agent-to-Agent) para comunicação horizontal (Agente-Agente) e MCP (Model Context Protocol) para comunicação vertical (Agente-Ferramenta), sobre HTTP(S) com JSON-RPC 2.0.
  * **Banco de Dados:** PostgreSQL para armazenamento persistente dos registros do Gateway, manifestos e métricas.
  * **Mensageria:** Redis Streams ou NATS para comunicação assíncrona e gerenciamento de estado de tarefas.
  * **Monitoramento:** Pilha Prometheus + Grafana para coleta de métricas de desempenho (latência, taxa de sucesso) em tempo real.
  * **LLMs (Motores de Raciocínio):** Modelos como Granite, Mistral e Llama2 (via API) para o Agente Principal.

## 5\. Como Começar

### Pré-requisitos

  * Python 3.9+
  * PostgreSQL
  * Redis ou NATS

### Instalação

1.  Clone este repositório:

    ```bash
    git clone https://github.com/seu-usuario/aegis.git
    cd aegis
    ```

2.  Crie e ative um ambiente virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4.  Configure suas variáveis de ambiente (crie um arquivo `.env`):

    ```env
    DATABASE_URL="postgresql://user:pass@localhost/aegis_db"
    REDIS_URL="redis://localhost:6379"
    # ... outras configurações
    ```

### Executando os Serviços

1.  **Iniciar o Gateway Agent:**

    ```bash
    uvicorn Aegis.core.gateway_agent.main:app --host 0.0.0.0 --port 8000
    ```

2.  **Iniciar o Principal Agent:**

    ```bash
    uvicorn Aegis.core.principal_agent.main:app --host 0.0.0.0 --port 8001
    ```

## 6\. Fluxo de Execução (Exemplo MVP)

1.  Um **Agente de Recurso** (ex: `WeatherAgent`) envia seus metadados (manifesto, schema da API, capacidades) para o endpoint `REGISTER_RESOURCE` do **Gateway Agent**.
2.  O **Gateway Agent** valida o recurso (executando testes de saúde) e o armazena, indexando-o por `id` e `capabilities`.
3.  Um usuário envia uma solicitação (ex: "Qual a previsão do tempo em São Paulo?") para o **Principal Agent**.
4.  O **Principal Agent** usa seu motor de raciocínio (ex: ReAct) para decompor a solicitação na tarefa `Task(description="obter_previsao_tempo", requirements=["weather", "location:São Paulo"])`.
5.  O **Principal Agent** consulta o **Gateway Agent** (via `QUERY_RESOURCES`) por agentes que satisfaçam os `requirements`.
6.  O **Gateway Agent** busca em seu `capability_index`, encontra o `WeatherAgent`, classifica-o com base em suas métricas de QoS (latência, taxa de sucesso) e retorna seus detalhes.
7.  O **Principal Agent** usa o protocolo A2A para delegar a `Task` ao endpoint do `WeatherAgent`.
8.  O `WeatherAgent` executa a tarefa e retorna o resultado.
9.  O **Principal Agent** atualiza suas métricas de execução no Gateway e retorna a resposta final ao usuário.

