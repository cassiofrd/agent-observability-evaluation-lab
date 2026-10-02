# Agent Observability & Evaluation Lab

Hands-on lab for AI agent observability, tracing, evaluation, and LLM-as-a-Judge using LangGraph, OpenAI, OpenTelemetry, and Streamlit.

The goal of this project is not to build a complex AI agent. Instead, it uses a deliberately simple agent so that the focus remains on two areas that become critical when agents move beyond prototypes:

- Observability
- Evaluation

The project demonstrates how to inspect agent execution, measure operational behavior, evaluate answer quality and tool usage, and detect regressions between different versions of an agent.

---

## Architecture

The agent is implemented with LangGraph and has access to two tools:

- `calculator`
- `get_order_status`

A request can therefore follow paths such as:

```text
User
  |
  v
Agent / LLM
  |
  +---- direct answer
  |
  +---- tool call
          |
          v
        Tool
          |
          v
        LLM
          |
          v
      Final answer