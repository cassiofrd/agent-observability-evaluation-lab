from langchain_core.messages import HumanMessage
from opentelemetry.trace import Status, StatusCode

from agent.graph import graph
from observability.otel import otel_tracer
from observability.storage import save_trace
from observability.tracer import tracer


def main():
    question = input("You: ")

    trace = tracer.start_trace(
        input_text=question
    )

    agent_span = tracer.start_span(
        "agent-run"
    )

    tracer.root_span = agent_span

    try:
        with otel_tracer.start_as_current_span(
            "agent-run"
        ) as otel_span:

            otel_span.set_attribute(
                "agent.input",
                question,
            )

            result = graph.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=question
                        )
                    ]
                }
            )

            final_message = (
                result["messages"][-1]
            )

            final_answer = (
                final_message.content
            )

            otel_span.set_attribute(
                "agent.output",
                final_answer,
            )

            otel_span.set_status(
                Status(
                    StatusCode.OK
                )
            )

        tracer.end_span(
            agent_span,
            status="success",
        )

        tracer.end_trace(
            status="success",
            output_text=final_answer,
        )

        save_trace(trace)

        print(
            f"\nAgent: {final_answer}"
        )

    except Exception as exc:
        tracer.end_span(
            agent_span,
            status="error",
        )

        tracer.end_trace(
            status="error",
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

        save_trace(trace)

        print(
            "\nAgent execution failed."
        )

        print(
            f"Error type: "
            f"{type(exc).__name__}"
        )

        print(
            f"Error message: {exc}"
        )

    print("\n--- TRACE ---")

    print(
        f"Trace ID: "
        f"{trace.trace_id}"
    )

    print(
        f"Status: "
        f"{trace.status}"
    )

    print(
        f"Duration: "
        f"{trace.duration_ms:.2f} ms"
    )

    print(
        f"Input: "
        f"{trace.input_text}"
    )

    print(
        f"Output: "
        f"{trace.output_text}"
    )

    print("\nSpans:")

    for span in trace.spans:
        print(
            f"\n- {span.name} | "
            f"{span.duration_ms:.2f} ms | "
            f"{span.status}"
        )

        print(
            f"    span_id: "
            f"{span.span_id}"
        )

        print(
            f"    parent_span_id: "
            f"{span.parent_span_id}"
        )

        for key, value in (
            span.attributes.items()
        ):
            print(
                f"    {key}: {value}"
            )


if __name__ == "__main__":
    main()