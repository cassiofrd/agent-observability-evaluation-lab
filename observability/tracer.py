import uuid
from datetime import datetime, timezone

from observability.models import Span, Trace


class Tracer:
    def __init__(self):
        self.current_trace: Trace | None = None
        self.root_span: Span | None = None

    def start_trace(self, input_text: str | None = None) -> Trace:
        trace = Trace(
            trace_id=str(uuid.uuid4()),
            start_time=datetime.now(timezone.utc),
            input_text=input_text,
        )

        self.current_trace = trace
        return trace

    def start_span(
        self,
        name: str,
        parent_span_id: str | None = None,
    ) -> Span:
        if self.current_trace is None:
            raise RuntimeError("No active trace.")

        span = Span(
            span_id=str(uuid.uuid4()),
            trace_id=self.current_trace.trace_id,
            parent_span_id=parent_span_id,
            name=name,
            start_time=datetime.now(timezone.utc),
        )

        self.current_trace.spans.append(span)

        return span

    def end_span(
        self,
        span: Span,
        status: str = "success",
    ) -> Span:
        span.end_time = datetime.now(timezone.utc)

        span.duration_ms = (
            span.end_time - span.start_time
        ).total_seconds() * 1000

        span.status = status

        return span

    def end_trace(
        self,
        status: str = "success",
        output_text: str | None = None,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> Trace:
        if self.current_trace is None:
            raise RuntimeError("No active trace.")

        self.current_trace.end_time = datetime.now(timezone.utc)

        self.current_trace.duration_ms = (
            self.current_trace.end_time
            - self.current_trace.start_time
        ).total_seconds() * 1000

        self.current_trace.status = status
        self.current_trace.output_text = output_text
        self.current_trace.error_type = error_type
        self.current_trace.error_message = error_message

        trace = self.current_trace

        self.current_trace = None
        self.root_span = None

        return trace


tracer = Tracer()