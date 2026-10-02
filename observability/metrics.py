import json
import statistics
from pathlib import Path

from observability.cost import calculate_trace_cost


TRACE_FILE = Path("data/traces.jsonl")


def load_traces() -> list[dict]:
    if not TRACE_FILE.exists():
        return []

    traces = []

    with TRACE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if line.strip():
                traces.append(
                    json.loads(line)
                )

    return traces


def percentile(
    values: list[float],
    p: float,
) -> float | None:
    if not values:
        return None

    values = sorted(values)

    index = (len(values) - 1) * p

    lower = int(index)

    upper = min(
        lower + 1,
        len(values) - 1,
    )

    if lower == upper:
        return values[lower]

    weight = index - lower

    return (
        values[lower] * (1 - weight)
        + values[upper] * weight
    )


def calculate_metrics(
    traces: list[dict],
) -> dict:
    if not traces:
        return {}

    latencies = [
        trace["duration_ms"]
        for trace in traces
        if trace.get("duration_ms")
        is not None
    ]

    successful = [
        trace
        for trace in traces
        if trace.get("status")
        == "success"
    ]

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    total_llm_calls = 0

    tool_usage: dict[str, int] = {}

    for trace in traces:
        for span in trace.get(
            "spans",
            [],
        ):
            attributes = span.get(
                "attributes",
                {},
            )

            if span.get("name") == "llm":
                total_llm_calls += 1

                total_input_tokens += (
                    attributes.get(
                        "llm.input_tokens",
                        0,
                    )
                    or 0
                )

                total_output_tokens += (
                    attributes.get(
                        "llm.output_tokens",
                        0,
                    )
                    or 0
                )

                total_tokens += (
                    attributes.get(
                        "llm.total_tokens",
                        0,
                    )
                    or 0
                )

            if span.get(
                "name",
                "",
            ).startswith("tool:"):
                tool_name = (
                    attributes.get(
                        "tool.name"
                    )
                )

                if tool_name:
                    tool_usage[
                        tool_name
                    ] = (
                        tool_usage.get(
                            tool_name,
                            0,
                        )
                        + 1
                    )

    traces_with_tools = []
    traces_without_tools = []

    for trace in traces:
        has_tool = any(
            span.get(
                "name",
                "",
            ).startswith("tool:")
            for span in trace.get(
                "spans",
                [],
            )
        )

        if has_tool:
            traces_with_tools.append(
                trace
            )
        else:
            traces_without_tools.append(
                trace
            )

    with_tool_latencies = [
        trace["duration_ms"]
        for trace in traces_with_tools
        if trace.get("duration_ms")
        is not None
    ]

    without_tool_latencies = [
        trace["duration_ms"]
        for trace
        in traces_without_tools
        if trace.get("duration_ms")
        is not None
    ]

    trace_costs = [
        calculate_trace_cost(trace)
        for trace in traces
    ]

    total_cost_usd = sum(
        trace_costs
    )

    request_count = len(traces)

    return {
        "request_count":
            request_count,

        "success_rate": (
            len(successful)
            / request_count
            if request_count
            else 0
        ),

        "average_latency_ms": (
            statistics.mean(
                latencies
            )
            if latencies
            else None
        ),

        "p50_latency_ms":
            percentile(
                latencies,
                0.50,
            ),

        "p95_latency_ms":
            percentile(
                latencies,
                0.95,
            ),

        "total_llm_calls":
            total_llm_calls,

        "average_llm_calls_per_request": (
            total_llm_calls
            / request_count
            if request_count
            else 0
        ),

        "total_input_tokens":
            total_input_tokens,

        "total_output_tokens":
            total_output_tokens,

        "total_tokens":
            total_tokens,

        "average_tokens_per_request": (
            total_tokens
            / request_count
            if request_count
            else 0
        ),

        "tool_usage":
            tool_usage,

        "requests_with_tools":
            len(
                traces_with_tools
            ),

        "requests_without_tools":
            len(
                traces_without_tools
            ),

        "average_latency_with_tools_ms": (
            statistics.mean(
                with_tool_latencies
            )
            if with_tool_latencies
            else None
        ),

        "average_latency_without_tools_ms": (
            statistics.mean(
                without_tool_latencies
            )
            if without_tool_latencies
            else None
        ),

        "total_cost_usd":
            total_cost_usd,

        "average_cost_per_request_usd": (
            total_cost_usd
            / request_count
            if request_count
            else 0
        ),
    }