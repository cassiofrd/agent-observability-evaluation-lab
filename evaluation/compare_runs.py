import json
import sys
from pathlib import Path


def load_run(path: str) -> dict:
    file_path = Path(path)

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def format_percent(value: float) -> str:
    return f"{value:.1%}"


def format_number(value: float) -> str:
    return f"{value:.2f}"


def compare_metric(
    name: str,
    baseline_value: float,
    candidate_value: float,
    is_percentage: bool = False,
    lower_is_better: bool = False,
):
    delta = (
        candidate_value
        - baseline_value
    )

    if lower_is_better:
        improved = delta < 0
    else:
        improved = delta > 0

    unchanged = delta == 0

    if unchanged:
        status = "UNCHANGED"
    elif improved:
        status = "IMPROVED"
    else:
        status = "REGRESSED"

    if is_percentage:
        baseline_text = format_percent(
            baseline_value
        )

        candidate_text = format_percent(
            candidate_value
        )

        delta_text = (
            f"{delta:+.1%}"
        )

    else:
        baseline_text = format_number(
            baseline_value
        )

        candidate_text = format_number(
            candidate_value
        )

        delta_text = (
            f"{delta:+.2f}"
        )

    print(
        f"{name}:"
    )

    print(
        f"  baseline:  "
        f"{baseline_text}"
    )

    print(
        f"  candidate: "
        f"{candidate_text}"
    )

    print(
        f"  delta:     "
        f"{delta_text}"
    )

    print(
        f"  status:    "
        f"{status}"
    )

    print()


def main():
    if len(sys.argv) != 3:
        print(
            "Usage:"
        )

        print(
            "python -m evaluation.compare_runs "
            "<baseline.json> "
            "<candidate.json>"
        )

        return

    baseline = load_run(
        sys.argv[1]
    )

    candidate = load_run(
        sys.argv[2]
    )

    baseline_summary = (
        baseline["summary"]
    )

    candidate_summary = (
        candidate["summary"]
    )

    print(
        "\n--- RUN COMPARISON ---\n"
    )

    compare_metric(
        "Answer accuracy",
        baseline_summary[
            "answer_accuracy"
        ],
        candidate_summary[
            "answer_accuracy"
        ],
        is_percentage=True,
    )

    compare_metric(
        "Tool selection accuracy",
        baseline_summary[
            "tool_selection_accuracy"
        ],
        candidate_summary[
            "tool_selection_accuracy"
        ],
        is_percentage=True,
    )

    compare_metric(
        "Tool argument accuracy",
        baseline_summary[
            "tool_argument_accuracy"
        ],
        candidate_summary[
            "tool_argument_accuracy"
        ],
        is_percentage=True,
    )

    compare_metric(
        "Trajectory accuracy",
        baseline_summary[
            "trajectory_accuracy"
        ],
        candidate_summary[
            "trajectory_accuracy"
        ],
        is_percentage=True,
    )

    compare_metric(
        "Average extra tool calls",
        baseline_summary[
            "average_extra_tool_calls"
        ],
        candidate_summary[
            "average_extra_tool_calls"
        ],
        lower_is_better=True,
    )

    compare_metric(
        "Average judge score",
        baseline_summary[
            "average_judge_score"
        ],
        candidate_summary[
            "average_judge_score"
        ],
    )

    compare_metric(
        "Judge pass rate",
        baseline_summary[
            "judge_pass_rate"
        ],
        candidate_summary[
            "judge_pass_rate"
        ],
        is_percentage=True,
    )

    compare_metric(
        "Task success rate",
        baseline_summary[
            "task_success_rate"
        ],
        candidate_summary[
            "task_success_rate"
        ],
        is_percentage=True,
    )


if __name__ == "__main__":
    main()