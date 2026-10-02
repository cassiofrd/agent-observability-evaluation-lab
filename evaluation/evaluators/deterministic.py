def evaluate_answer_contains(
    actual_answer: str,
    expected_text: str,
) -> bool:
    return (
        expected_text.lower()
        in actual_answer.lower()
    )


def evaluate_tool_selection(
    actual_tool: str | None,
    expected_tool: str | None,
) -> bool:
    return actual_tool == expected_tool


def evaluate_tool_arguments(
    actual_args: dict | None,
    expected_args: dict | None,
) -> bool:
    if expected_args is None:
        return actual_args is None

    if actual_args is None:
        return False

    return actual_args == expected_args