import json
from dataclasses import asdict
from pathlib import Path

from observability.models import Trace


TRACE_FILE = Path("data/traces.jsonl")


def save_trace(trace: Trace) -> None:
    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_FILE.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                asdict(trace),
                default=str,
                ensure_ascii=False,
            )
            + "\n"
        )