import sys
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


from observability.cost import calculate_trace_cost
from observability.metrics import calculate_metrics, load_traces


st.set_page_config(
    page_title="Agent Observability Dashboard",
    layout="wide",
)


st.title("Agent Observability Dashboard")


traces = load_traces()

if not traces:
    st.warning("No traces found yet.")
    st.stop()


metrics = calculate_metrics(traces)


# ---------------------------------------------------------
# High-level metrics
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Requests",
        metrics["request_count"],
    )

with col2:
    st.metric(
        "Success Rate",
        f"{metrics['success_rate'] * 100:.1f}%",
    )

with col3:
    st.metric(
        "Average Latency",
        f"{metrics['average_latency_ms'] / 1000:.2f} s",
    )

with col4:
    st.metric(
        "P95 Latency",
        f"{metrics['p95_latency_ms'] / 1000:.2f} s",
    )


st.divider()


col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "Total Tokens",
        metrics["total_tokens"],
    )

with col6:
    st.metric(
        "LLM Calls",
        metrics["total_llm_calls"],
    )

with col7:
    st.metric(
        "Total Cost",
        f"${metrics['total_cost_usd']:.5f}",
    )

with col8:
    st.metric(
        "Avg Cost / Request",
        f"${metrics['average_cost_per_request_usd']:.5f}",
    )


col9, col10 = st.columns(2)

with col9:
    st.metric(
        "Requests With Tools",
        metrics["requests_with_tools"],
    )

with col10:
    st.metric(
        "Requests Without Tools",
        metrics["requests_without_tools"],
    )

# ---------------------------------------------------------
# Latency
# ---------------------------------------------------------

st.divider()

st.subheader("Latency Comparison")

latency_data = {
    "With Tools": (
        metrics["average_latency_with_tools_ms"] or 0
    ) / 1000,
    "Without Tools": (
        metrics["average_latency_without_tools_ms"] or 0
    ) / 1000,
}

st.bar_chart(latency_data)


# ---------------------------------------------------------
# Tool usage
# ---------------------------------------------------------

st.subheader("Tool Usage")

if metrics["tool_usage"]:
    st.bar_chart(metrics["tool_usage"])
else:
    st.info("No tool calls found.")


# ---------------------------------------------------------
# Token usage
# ---------------------------------------------------------

st.divider()

st.subheader("Token Usage")

token_data = {
    "Input Tokens": metrics["total_input_tokens"],
    "Output Tokens": metrics["total_output_tokens"],
}

st.bar_chart(token_data)


# ---------------------------------------------------------
# Trace Explorer
# ---------------------------------------------------------

st.divider()

st.subheader("Trace Explorer")


trace_options = {
    trace["trace_id"]: trace
    for trace in traces
}

selected_trace_id = st.selectbox(
    "Select a trace",
    options=list(trace_options.keys()),
)

selected_trace = trace_options[selected_trace_id]


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Status",
        selected_trace.get("status", "unknown"),
    )

with col2:
    duration_ms = selected_trace.get("duration_ms") or 0

    st.metric(
        "Duration",
        f"{duration_ms / 1000:.2f} s",
    )

with col3:
    span_count = len(
        selected_trace.get("spans", [])
    )

    st.metric(
        "Spans",
        span_count,
    )


trace_tokens = 0

for span in selected_trace.get("spans", []):
    if span.get("name") == "llm":
        attributes = span.get("attributes", {})

        trace_tokens += (
            attributes.get(
                "llm.total_tokens",
                0,
            )
            or 0
        )


with col4:
    st.metric(
        "Tokens",
        trace_tokens,
    )


trace_cost = calculate_trace_cost(
    selected_trace
)

with col5:
    st.metric(
        "Cost",
        f"${trace_cost:.5f}",
    )


# ---------------------------------------------------------
# Input / Output
# ---------------------------------------------------------

st.markdown("### Input")

input_text = selected_trace.get("input_text")

if input_text:
    st.write(input_text)
else:
    st.info("No input recorded.")


st.markdown("### Output")

output_text = selected_trace.get("output_text")

if output_text:
    st.write(output_text)
else:
    st.info("No output recorded.")


# ---------------------------------------------------------
# Error information
# ---------------------------------------------------------

if selected_trace.get("status") == "error":
    st.markdown("### Error")

    error_type = selected_trace.get(
        "error_type",
        "UnknownError",
    )

    error_message = selected_trace.get(
        "error_message",
        "No error message recorded.",
    )

    st.error(
        f"{error_type}: {error_message}"
    )


# ---------------------------------------------------------
# Span tree
# ---------------------------------------------------------

st.markdown("### Span Tree")


spans = selected_trace.get("spans", [])


children_by_parent = {}

for span in spans:
    parent_id = span.get("parent_span_id")

    if parent_id not in children_by_parent:
        children_by_parent[parent_id] = []

    children_by_parent[parent_id].append(span)


def render_span(
    span: dict,
    depth: int = 0,
) -> None:
    duration = span.get("duration_ms") or 0
    status = span.get("status", "unknown")
    name = span.get("name", "unknown")

    indent = " " * depth

    label = (
        f"{indent}{name} "
        f"— {duration:.2f} ms "
        f"— {status}"
    )

    with st.expander(label):
        st.write(
            f"**Span ID:** "
            f"{span.get('span_id')}"
        )

        st.write(
            f"**Parent Span ID:** "
            f"{span.get('parent_span_id')}"
        )

        attributes = span.get(
            "attributes",
            {},
        )

        if attributes:
            st.markdown("#### Attributes")

            for key, value in attributes.items():
                st.write(
                    f"**{key}:**",
                    value,
                )
        else:
            st.info(
                "No attributes recorded."
            )

    child_spans = children_by_parent.get(
        span.get("span_id"),
        [],
    )

    for child in child_spans:
        render_span(
            child,
            depth + 1,
        )


root_spans = [
    span
    for span in spans
    if span.get("parent_span_id") is None
]


if root_spans:
    for root_span in root_spans:
        render_span(root_span)
else:
    st.warning(
        "No root spans found for this trace."
    )