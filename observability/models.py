from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Span:
    span_id: str
    trace_id: str
    name: str
    start_time: datetime
    parent_span_id: str | None = None
    end_time: datetime | None = None
    duration_ms: float | None = None
    status: str = "running"
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Trace:
    trace_id: str
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None
    status: str = "running"

    input_text: str | None = None
    output_text: str | None = None

    error_type: str | None = None
    error_message: str | None = None

    spans: list[Span] = field(default_factory=list)