def extract_tool_trajectory(
    trace,
) -> list[str]:
    trajectory = []

    for span in trace.spans:
        if not span.name.startswith("tool:"):
            continue

        tool_name = span.attributes.get(
            "tool.name"
        )

        if tool_name:
            trajectory.append(
                tool_name
            )

    return trajectory


def evaluate_tool_trajectory(
    actual_trajectory: list[str],
    expected_trajectory: list[str],
) -> bool:
    return (
        actual_trajectory
        == expected_trajectory
    )


def calculate_extra_tool_calls(
    actual_trajectory: list[str],
    expected_trajectory: list[str],
) -> int:
    return max(
        0,
        len(actual_trajectory)
        - len(expected_trajectory),
    )