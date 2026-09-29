# Agent Observability & Evaluation Lab

A hands-on project focused on understanding **observability** and **evaluation for AI agents**.

The goal of this repository is not to build a complex agent. Instead, it uses a deliberately simple LangGraph-based agent so that most of the engineering effort can be concentrated on understanding how to **observe, measure, debug, and evaluate agent behavior**.

## Objectives

This project explores two complementary areas:

### 1. Agent Observability

Understand what happens during an agent execution.

Topics include:

- Traces and spans
- Trace IDs and span IDs
- Parent-child relationships between spans
- LLM calls
- Tool calls
- Tool arguments and outputs
- Node execution
- Latency
- Token usage
- Estimated cost
- Errors and exceptions
- Retries
- Agent execution steps
- Success and failure rates
- P50 and P95 latency
- Trace exploration and debugging

The first version of the observability layer will be implemented manually in order to understand the underlying concepts.

Later, the project may integrate standard observability technologies such as **OpenTelemetry**.

---

### 2. Agent Evaluation

Understand whether the agent performed well.

Evaluation topics include:

- Task success
- Answer correctness
- Ground truth comparison
- Tool selection accuracy
- Tool argument accuracy
- Trajectory evaluation
- Groundedness
- Relevance
- LLM-as-a-Judge
- Deterministic evaluators
- Heuristic evaluators
- Adversarial test cases
- Regression testing
- Comparison between agent versions
- Quality vs latency vs cost trade-offs

---

## Core Idea

The agent itself should remain intentionally simple.

Example architecture:

```text
User
  |
  v
LangGraph Agent
  |
  +-- Router
  |
  +-- Tool A
  |
  +-- Tool B
  |
  +-- Tool C
  |
  v
Final Answer
```

The interesting part of the project is everything around the execution:

```text
                     OBSERVABILITY

User Request
     |
     v
   Trace
     |
     +-- Router Span
     |
     +-- LLM Span
     |     +-- latency
     |     +-- tokens
     |     +-- model
     |
     +-- Tool Span
     |     +-- tool name
     |     +-- arguments
     |     +-- duration
     |     +-- result
     |
     +-- LLM Span
     |
     +-- Final Answer
```

---

## Planned Architecture

```text
agent-observability-evaluation-lab/
|
|-- agent/
|   |-- graph.py
|   |-- state.py
|   |-- tools.py
|
|-- observability/
|   |-- models.py
|   |-- tracer.py
|   |-- metrics.py
|   |-- cost.py
|
|-- evaluation/
|   |-- datasets/
|   |
|   |-- evaluators/
|   |   |-- deterministic.py
|   |   |-- trajectory.py
|   |   |-- llm_judge.py
|   |
|   |-- runner.py
|   |-- compare_runs.py
|
|-- dashboard/
|   |-- app.py
|
|-- tests/
|
|-- .env.example
|-- requirements.txt
|-- README.md
```

The project structure may evolve as new concepts are introduced.

---

## Phase 1 — Simple Agent

Build a small LangGraph agent with only a few tools.

The agent should be simple enough that its behavior is easy to understand and inspect.

Possible tools:

- Calculator
- Order lookup
- Policy lookup
- Simple knowledge lookup

The focus is not agent complexity.

---

## Phase 2 — Manual Observability

Implement a lightweight tracing system from scratch.

Example trace information:

```json
{
  "trace_id": "abc123",
  "span_id": "span456",
  "parent_span_id": "span001",
  "component": "tool",
  "name": "get_order_status",
  "duration_ms": 312,
  "status": "success"
}
```

This phase is intended to make concepts such as traces, spans, events, and attributes concrete before introducing external observability frameworks.

---

## Phase 3 — Metrics

Collect operational metrics such as:

- Total requests
- Successful requests
- Failed requests
- Average latency
- P50 latency
- P95 latency
- Average number of agent steps
- Tool usage
- Token consumption
- Estimated LLM cost

Example:

```text
Requests              120
Success Rate           96%
Average Latency       1.7 s
P95 Latency           3.4 s
Average Tokens         846
Estimated Cost       $0.82
```

---

## Phase 4 — Trace Explorer

Build a simple dashboard for exploring individual executions.

Example:

```text
Trace: f81c...

Total duration: 2.14 s

Agent
|
+-- router                  42 ms
|
+-- LLM                   1.08 s
|
+-- get_order_status       318 ms
|
+-- LLM                    702 ms
```

The goal is to understand exactly where time, tokens, errors, and agent decisions occur.

---

## Phase 5 — Evaluation Dataset

Create a small evaluation dataset containing:

- User question
- Expected answer
- Expected tool
- Expected tool arguments
- Expected trajectory when relevant
- Test category

Example:

```json
{
  "id": "test_001",
  "question": "What is the status of order 1024?",
  "expected_answer": "In transit",
  "expected_tools": [
    "get_order_status"
  ],
  "expected_tool_args": {
    "order_id": "1024"
  }
}
```

The dataset should also include edge cases and adversarial examples.

---

## Phase 6 — Deterministic Evaluation

Implement evaluators that can be calculated directly in code.

Examples:

```text
expected_tool == actual_tool
```

```text
expected_order_id == actual_order_id
```

Metrics may include:

- Tool selection accuracy
- Tool argument accuracy
- Exact match
- Task success
- Number of unnecessary tool calls

---

## Phase 7 — LLM-as-a-Judge

Use an LLM to evaluate dimensions that are difficult to measure using deterministic rules.

Possible dimensions:

- Correctness
- Relevance
- Completeness
- Groundedness

Conceptually:

```text
Question
+
Reference Answer
+
Agent Answer
        |
        v
   Judge LLM
        |
        v
      Score
```

The project will also explore the limitations and potential biases of LLM-based evaluators.

---

## Phase 8 — Trajectory Evaluation

Evaluate not only the final answer, but also how the agent reached it.

For example:

```text
Expected:

User
  |
get_order_status
  |
get_refund_policy
  |
Answer
```

versus:

```text
Actual:

User
  |
get_refund_policy
  |
get_order_status
  |
get_order_status
  |
calculate_refund
  |
Answer
```

Both executions might produce the same final answer, but the second trajectory is more expensive and unnecessarily complex.

Possible metrics:

- Correct tool sequence
- Number of steps
- Unnecessary tool calls
- Failed calls
- Retries
- Trajectory efficiency

---

## Phase 9 — Experiment Comparison

Compare multiple versions of the same agent.

For example:

| Metric | Agent V1 | Agent V2 |
|---|---:|---:|
| Task Success | 78% | 91% |
| Tool Accuracy | 86% | 95% |
| Groundedness | 88% | 94% |
| Avg Latency | 1.5 s | 1.9 s |
| Avg Tokens | 920 | 1,180 |

This allows the project to explore an important engineering question:

> Is a more accurate agent still better if it is slower and more expensive?

Agent quality is inherently multi-objective.

---

## Observability vs Evaluation

A central concept explored in this repository is the difference between observability and evaluation.

```text
OBSERVABILITY

"What happened during this execution?"

- traces
- spans
- latency
- tokens
- cost
- errors
- tool calls
- retries
```

```text
EVALUATION

"Was this execution good?"

- correctness
- task success
- relevance
- groundedness
- tool accuracy
- trajectory quality
```

Observability helps explain **why** something happened.

Evaluation helps determine **whether the result was good**.

Together they provide a much more complete understanding of agent behavior.

---

## Technologies

Initial stack:

- Python
- LangGraph
- OpenAI / Azure OpenAI
- Pandas
- Streamlit

Possible later additions:

- OpenTelemetry
- Azure AI Foundry Evaluation
- External tracing / observability platforms

---

## Learning Goals

By the end of this project, the goal is to be comfortable discussing and implementing concepts such as:

- Agent tracing
- Traces and spans
- Agent observability
- LLM telemetry
- Token and cost tracking
- Latency analysis
- Agent evaluation
- Ground truth
- Deterministic evaluators
- LLM-as-a-Judge
- Groundedness
- Trajectory evaluation
- Regression testing
- Offline evaluation
- Agent experiments
- Quality / latency / cost trade-offs

The repository is intentionally designed as a **learning lab**, prioritizing clarity and experimentation over production complexity.
