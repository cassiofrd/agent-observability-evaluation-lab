import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from opentelemetry.trace import Status, StatusCode

from agent.state import AgentState
from agent.tools import calculator, get_order_status
from observability.otel import otel_tracer
from observability.tracer import tracer


load_dotenv(override=True)


tools = [
    calculator,
    get_order_status,
]


llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
    temperature=0,
    reasoning_effort="none",
)


llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """
You are a simple test agent used for an observability lab.

Rules:
- Always use the calculator tool for arithmetic operations.
- Always use get_order_status when the user asks about an order.
- Do not calculate arithmetic yourself when the calculator tool can be used.
"""


def call_model(state: AgentState):
    parent_span_id = (
        tracer.root_span.span_id
        if tracer.root_span
        else None
    )

    span = tracer.start_span(
        "llm",
        parent_span_id=parent_span_id,
    )

    model_name = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6",
    )

    span.attributes["llm.model"] = model_name

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        # OpenTelemetry span for this LLM call.
        # Because agent-run is already the current OTel span,
        # this span automatically becomes its child.
        with otel_tracer.start_as_current_span(
            "llm"
        ) as otel_span:

            otel_span.set_attribute(
                "llm.model",
                model_name,
            )

            response = llm_with_tools.invoke(
                messages
            )

            usage = getattr(
                response,
                "usage_metadata",
                None,
            )

            if usage:
                input_tokens = (
                    usage.get(
                        "input_tokens",
                        0,
                    )
                    or 0
                )

                output_tokens = (
                    usage.get(
                        "output_tokens",
                        0,
                    )
                    or 0
                )

                total_tokens = (
                    usage.get(
                        "total_tokens",
                        0,
                    )
                    or 0
                )

                # Manual tracer attributes
                span.attributes[
                    "llm.input_tokens"
                ] = input_tokens

                span.attributes[
                    "llm.output_tokens"
                ] = output_tokens

                span.attributes[
                    "llm.total_tokens"
                ] = total_tokens

                # OpenTelemetry attributes
                otel_span.set_attribute(
                    "llm.input_tokens",
                    input_tokens,
                )

                otel_span.set_attribute(
                    "llm.output_tokens",
                    output_tokens,
                )

                otel_span.set_attribute(
                    "llm.total_tokens",
                    total_tokens,
                )

            tool_calls = (
                response.tool_calls
            )

            span.attributes[
                "llm.tool_calls"
            ] = tool_calls

            otel_span.set_attribute(
                "llm.tool_call_count",
                len(tool_calls),
            )

            otel_span.set_status(
                Status(
                    StatusCode.OK
                )
            )

        tracer.end_span(
            span,
            status="success",
        )

        return {
            "messages": [response]
        }

    except Exception as exc:
        span.attributes[
            "error.type"
        ] = type(exc).__name__

        span.attributes[
            "error.message"
        ] = str(exc)

        tracer.end_span(
            span,
            status="error",
        )

        raise


builder = StateGraph(
    AgentState
)

builder.add_node(
    "agent",
    call_model,
)

builder.add_node(
    "tools",
    ToolNode(tools),
)

builder.add_edge(
    START,
    "agent",
)

builder.add_conditional_edges(
    "agent",
    tools_condition,
)

builder.add_edge(
    "tools",
    "agent",
)


graph = builder.compile()