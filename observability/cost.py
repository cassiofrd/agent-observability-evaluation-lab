MODEL_PRICING = {
    "gpt-5.6": {
        "input_per_million": 4.00,
        "output_per_million": 20.00,
    },
    "gpt-5.6-sol": {
        "input_per_million": 4.00,
        "output_per_million": 20.00,
    },
}


def calculate_llm_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return 0.0

    input_cost = (
        input_tokens
        / 1_000_000
        * pricing["input_per_million"]
    )

    output_cost = (
        output_tokens
        / 1_000_000
        * pricing["output_per_million"]
    )

    return input_cost + output_cost


def calculate_trace_cost(trace: dict) -> float:
    total_cost = 0.0

    for span in trace.get("spans", []):
        if span.get("name") != "llm":
            continue

        attributes = span.get(
            "attributes",
            {},
        )

        model = attributes.get(
            "llm.model",
            "gpt-5.6",
        )

        input_tokens = (
            attributes.get(
                "llm.input_tokens",
                0,
            )
            or 0
        )

        output_tokens = (
            attributes.get(
                "llm.output_tokens",
                0,
            )
            or 0
        )

        total_cost += calculate_llm_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    return total_cost