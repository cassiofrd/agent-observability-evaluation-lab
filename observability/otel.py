from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


resource = Resource.create(
    {
        "service.name": "agent-observability-evaluation-lab",
    }
)


provider = TracerProvider(
    resource=resource,
)


console_exporter = ConsoleSpanExporter()


span_processor = BatchSpanProcessor(
    console_exporter,
)


provider.add_span_processor(
    span_processor,
)


trace.set_tracer_provider(
    provider,
)


otel_tracer = trace.get_tracer(
    "agent-observability-evaluation-lab"
)