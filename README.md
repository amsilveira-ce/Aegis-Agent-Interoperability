
# Aegis: Implementing the DAWN Framework

Aegis is the reference implementation of **DAWN (Distributed Agent Workflow Network)** — an architectural framework designed to enable **universal interoperability, discovery, and collaboration among heterogeneous Artificial Intelligence agents**.

---

## 1. The Problem: AI Silos

Today’s AI landscape is fragmented. Autonomous agents operate within isolated ecosystems (such as LangChain, CrewAI, etc.), unable to collaborate with external agents. This leads to redundant development and limits the complexity of solvable problems.
DAWN is proposed to break these silos, creating a communication standard for a truly collaborative AI ecosystem.

---

## 2. The Solution: DAWN Framework

DAWN proposes a **top-down orchestration model**, centered around two main components, to build a **global and meritocratic marketplace of AI capabilities**.

### Core Architecture

The DAWN architecture consists of three main pillars:

1. **Principal Agent:** The central orchestrator. It receives user requests, decomposes them into tasks, plans execution, and manages context.
2. **Gateway Agent:** The service discovery registry. Acts as an “intelligent catalog” where Resource Agents (tools or other agents) register and are discovered based on their capabilities and performance metrics (QoS).
3. **Resource Agent:** Any specialized agent or tool (e.g., a calculator, web search agent, or specialized AI model) that provides a specific capability.

---

## 3. Aegis Core Components

This Aegis implementation is divided into the following main components, reflecting the DAWN blueprint.

### 3.1. Principal Agent (`Aegis/core/principal_agent`)

Acts as the central brain of orchestration.

**Design Rationale:**

* **Flexible Operation Modes:** Supports `NO_LLM`, `ASSISTED` (Copilot), `AGENT`, and `HYBRID` modes, allowing transitions between deterministic and autonomous workflows.
* **Context Management:** Maintains a hierarchical context (`conversation_history`, `user_preferences`, `task_history`, `memory_bank`) for personalization and continuity across complex tasks.
* **Reasoning Strategies:** Designed to implement multiple “reasoning engines” (e.g., ReAct, ReWOO, ToT) for task decomposition.
* **Local Resource Cache:** Keeps a local cache of resources to reduce network overhead from frequent Gateway queries.

**Schema (`principalAgent.py`):**

* `mode: OperationalMode`
* `gateway_agents: List[GatewayAgent]`
* `local_resources: Dict[str, Resource]`
* `task_queue: List[Task]`
* `execution_history: List[Dict]`
* `context: Dict`
* `reasoning_strategies: Dict`

---

### 3.2. Gateway Agent (`Aegis/core/gateway_agent`)

Manages registration, validation, and intelligent discovery of all resources available in the network.

**Design Rationale:**

* **Dual Index Registry:** Uses a `registry` (for O(1) lookup by ID) and a `capability_index` (for O(1) discovery by capability) — essential for high performance.
* **Performance Tracking (QoS):** Each registered resource includes its own performance metrics (`performance_metrics`, `success_rate`, `avg_response_time`). This allows the Gateway to act as an intelligent selector, ranking resources not only by capability but also by historical performance.
* **Resource Validation:** Includes `test_results` and `is_active`, allowing failed resources to be gracefully deactivated without removal — ensuring system robustness.

**Schema (`gatewayAgent.py` and `gatewayAgent_schemas.py`):**

* `registry: Dict[str, RegisteredResource]`
* `capability_index: Dict[str, List[str]]`
* `security_filters: List[Callable]`
* `gateway_metrics: Dict`
* `RegisteredResource` (Schema):

  * `id: str`
  * `capabilities: List[str]`
  * `endpoint: str`
  * `api_schema: Dict[str, Any]`
  * `manifest: Dict[str, Any]`
  * `performance_metrics: Dict[str, float]`
  * `is_active: bool`

---

## 4. Technology Stack (MVP)

The methodology for this MVP uses the following technologies:

* **Backend:** Python (FastAPI) and Node.js for agent services.
* **Protocols:** A2A (Agent-to-Agent) for horizontal communication (Agent-Agent) and MCP (Model Context Protocol) for vertical communication (Agent-Tool), over HTTP(S) with JSON-RPC 2.0.
* **Database:** PostgreSQL for persistent storage of Gateway registries, manifests, and metrics.
* **Messaging:** Redis Streams or NATS for asynchronous communication and task state management.
* **Monitoring:** Prometheus + Grafana stack for real-time performance metrics (latency, success rate).
* **LLMs (Reasoning Engines):** Models such as Granite, Mistral, and Llama2 (via API) for the Principal Agent.

---

## 5. Getting Started

### Prerequisites

* Python 3.9+
* PostgreSQL
* Redis or NATS

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/aegis.git
   cd aegis
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables (create a `.env` file):

   ```env
   DATABASE_URL="postgresql://user:pass@localhost/aegis_db"
   REDIS_URL="redis://localhost:6379"
   # ... other configurations
   ```

---

### Running the Services

1. **Start the Gateway Agent:**

   ```bash
   uvicorn Aegis.core.gateway_agent.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the Principal Agent:**

   ```bash
   uvicorn Aegis.core.principal_agent.main:app --host 0.0.0.0 --port 8001
   ```

---

## 6. Execution Flow (MVP Example)

1. A **Resource Agent** (e.g., `WeatherAgent`) sends its metadata (manifest, API schema, capabilities) to the **Gateway Agent**’s `REGISTER_RESOURCE` endpoint.
2. The **Gateway Agent** validates the resource (performing health checks) and stores it, indexing by both `id` and `capabilities`.
3. A user sends a request (e.g., “What’s the weather forecast in São Paulo?”) to the **Principal Agent**.
4. The **Principal Agent** uses its reasoning engine (e.g., ReAct) to decompose the request into a task:
   `Task(description="get_weather_forecast", requirements=["weather", "location:São Paulo"])`.
5. The **Principal Agent** queries the **Gateway Agent** (via `QUERY_RESOURCES`) for agents that satisfy the `requirements`.
6. The **Gateway Agent** looks up its `capability_index`, finds the `WeatherAgent`, ranks it based on QoS metrics (latency, success rate), and returns its details.
7. The **Principal Agent** uses the A2A protocol to delegate the `Task` to the `WeatherAgent`’s endpoint.
8. The `WeatherAgent` executes the task and returns the result.
9. The **Principal Agent** updates execution metrics in the Gateway and returns the final response to the user.


