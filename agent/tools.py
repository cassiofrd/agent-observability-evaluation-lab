from typing import Literal

from langchain_core.tools import tool
from opentelemetry.trace import Status, StatusCode

from observability.otel import otel_tracer
from observability.tracer import tracer


def get_parent_span_id() -> str | None:
    if tracer.root_span is None:
        return None

    return tracer.root_span.span_id


@tool
def calculator(
    a: float,
    b: float,
    operation: Literal[
        "add",
        "subtract",
        "multiply",
        "divide",
    ],
) -> float:
    """Perform a basic arithmetic operation between two numbers."""

    span = tracer.start_span(
        "tool:calculator",
        parent_span_id=get_parent_span_id(),
    )

    span.attributes["tool.name"] = "calculator"

    span.attributes["tool.arguments"] = {
        "a": a,
        "b": b,
        "operation": operation,
    }

    try:
        with otel_tracer.start_as_current_span(
            "tool:calculator"
        ) as otel_span:

            otel_span.set_attribute(
                "tool.name",
                "calculator",
            )

            otel_span.set_attribute(
                "tool.a",
                a,
            )

            otel_span.set_attribute(
                "tool.b",
                b,
            )

            otel_span.set_attribute(
                "tool.operation",
                operation,
            )

            if operation == "add":
                result = a + b

            elif operation == "subtract":
                result = a - b

            elif operation == "multiply":
                result = a * b

            elif operation == "divide":
                if b == 0:
                    raise ValueError(
                        "Division by zero is not allowed."
                    )

                result = a / b

            else:
                raise ValueError(
                    f"Unsupported operation: {operation}"
                )

            span.attributes["tool.result"] = result

            otel_span.set_attribute(
                "tool.result",
                result,
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

        return result

    except Exception as exc:
        span.attributes["error.type"] = (
            type(exc).__name__
        )

        span.attributes["error.message"] = (
            str(exc)
        )

        tracer.end_span(
            span,
            status="error",
        )

        raise


@tool
def get_order_status(order_id: str) -> str:
    """Return the current status of an order."""

    span = tracer.start_span(
        "tool:get_order_status",
        parent_span_id=get_parent_span_id(),
    )

    span.attributes["tool.name"] = (
        "get_order_status"
    )

    span.attributes["tool.arguments"] = {
        "order_id": order_id
    }

    try:
        with otel_tracer.start_as_current_span(
            "tool:get_order_status"
        ) as otel_span:

            otel_span.set_attribute(
                "tool.name",
                "get_order_status",
            )

            otel_span.set_attribute(
                "tool.order_id",
                order_id,
            )

            orders = {
                "1001": "processing",
                "1002": "shipped",
                "1003": "delivered",
                "1004": "cancelled",
            }

            status = orders.get(order_id)

            if status is None:
                result = (
                    f"Order {order_id} was not found."
                )
            else:
                result = (
                    f"Order {order_id} is {status}."
                )

            span.attributes["tool.result"] = result

            otel_span.set_attribute(
                "tool.result",
                result,
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

        return result

    except Exception as exc:
        span.attributes["error.type"] = (
            type(exc).__name__
        )

        span.attributes["error.message"] = (
            str(exc)
        )

        tracer.end_span(
            span,
            status="error",
        )

        raise