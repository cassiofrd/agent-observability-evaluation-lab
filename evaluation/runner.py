import json
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import HumanMessage

from agent.graph import graph
from evaluation.evaluators.deterministic import (
    evaluate_answer_contains,
    evaluate_tool_arguments,
    evaluate_tool_selection,
)
from evaluation.evaluators.llm_judge import (
    evaluate_with_llm_judge,
)
from evaluation.evaluators.trajectory import (
    calculate_extra_tool_calls,
    evaluate_tool_trajectory,
    extract_tool_trajectory,
)
from observability.tracer import tracer


DATASET_PATH = Path(
    "evaluation/datasets/agent_eval.json"
)

RESULTS_DIR = Path(
    "evaluation/results"
)


def load_dataset() -> list[dict]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_first_tool_call(
    trace,
) -> tuple[str | None, dict | None]:
    for span in trace.spans:
        if not span.name.startswith("tool:"):
            continue

        tool_name = span.attributes.get(
            "tool.name"
        )

        tool_args = span.attributes.get(
            "tool.arguments"
        )

        return tool_name, tool_args

    return None, None


def run_case(case: dict) -> dict:
    question = case["question"]

    trace = tracer.start_trace(
        input_text=question
    )

    agent_span = tracer.start_span(
        "agent-run"
    )

    tracer.root_span = agent_span

    try:
        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=question
                    )
                ]
            }
        )

        final_answer = (
            result["messages"][-1].content
        )

        tracer.end_span(
            agent_span,
            status="success",
        )

        tracer.end_trace(
            status="success",
            output_text=final_answer,
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

        final_answer = ""

    actual_tool, actual_args = (
        extract_first_tool_call(trace)
    )

    actual_trajectory = (
        extract_tool_trajectory(trace)
    )

    answer_ok = evaluate_answer_contains(
        final_answer,
        case["expected_answer_contains"],
    )

    tool_ok = evaluate_tool_selection(
        actual_tool,
        case["expected_tool"],
    )

    args_ok = evaluate_tool_arguments(
        actual_args,
        case["expected_args"],
    )

    trajectory_ok = evaluate_tool_trajectory(
        actual_trajectory,
        case["expected_trajectory"],
    )

    extra_tool_calls = (
        calculate_extra_tool_calls(
            actual_trajectory,
            case["expected_trajectory"],
        )
    )

    judge_result = evaluate_with_llm_judge(
        question=question,
        expected_answer=(
            case["expected_answer_contains"]
        ),
        actual_answer=final_answer,
    )

    judge_score = (
        judge_result["score"]
    )

    judge_passed = (
        judge_result["passed"]
    )

    judge_reason = (
        judge_result["reason"]
    )

    task_success = (
        answer_ok
        and tool_ok
        and args_ok
        and trajectory_ok
    )

    return {
        "id":
            case["id"],

        "question":
            question,

        "expected_answer_contains":
            case["expected_answer_contains"],

        "expected_tool":
            case["expected_tool"],

        "expected_args":
            case["expected_args"],

        "expected_trajectory":
            case["expected_trajectory"],

        "actual_answer":
            final_answer,

        "actual_tool":
            actual_tool,

        "actual_args":
            actual_args,

        "actual_trajectory":
            actual_trajectory,

        "answer_ok":
            answer_ok,

        "tool_ok":
            tool_ok,

        "args_ok":
            args_ok,

        "trajectory_ok":
            trajectory_ok,

        "extra_tool_calls":
            extra_tool_calls,

        "judge_score":
            judge_score,

        "judge_passed":
            judge_passed,

        "judge_reason":
            judge_reason,

        "task_success":
            task_success,
    }


def calculate_summary(
    results: list[dict],
) -> dict:
    total = len(results)

    if total == 0:
        return {
            "total_cases": 0,
            "answer_accuracy": 0,
            "tool_selection_accuracy": 0,
            "tool_argument_accuracy": 0,
            "trajectory_accuracy": 0,
            "average_extra_tool_calls": 0,
            "average_judge_score": 0,
            "judge_pass_rate": 0,
            "task_success_rate": 0,
        }

    answer_passed = sum(
        1
        for result in results
        if result["answer_ok"]
    )

    tool_passed = sum(
        1
        for result in results
        if result["tool_ok"]
    )

    args_passed = sum(
        1
        for result in results
        if result["args_ok"]
    )

    trajectory_passed = sum(
        1
        for result in results
        if result["trajectory_ok"]
    )

    task_passed = sum(
        1
        for result in results
        if result["task_success"]
    )

    judge_passed = sum(
        1
        for result in results
        if result["judge_passed"]
    )

    total_extra_tool_calls = sum(
        result["extra_tool_calls"]
        for result in results
    )

    total_judge_score = sum(
        result["judge_score"]
        for result in results
    )

    return {
        "total_cases":
            total,

        "answer_accuracy":
            answer_passed / total,

        "tool_selection_accuracy":
            tool_passed / total,

        "tool_argument_accuracy":
            args_passed / total,

        "trajectory_accuracy":
            trajectory_passed / total,

        "average_extra_tool_calls":
            total_extra_tool_calls / total,

        "average_judge_score":
            total_judge_score / total,

        "judge_pass_rate":
            judge_passed / total,

        "task_success_rate":
            task_passed / total,
    }


def save_results(
    results: list[dict],
    summary: dict,
) -> Path:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        RESULTS_DIR
        / f"eval_run_{timestamp}.json"
    )

    payload = {
        "created_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "summary":
            summary,

        "results":
            results,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_path


def main():
    dataset = load_dataset()

    results = []

    for case in dataset:
        print(
            f"Running {case['id']}..."
        )

        result = run_case(case)

        results.append(result)

    print(
        "\n--- EVALUATION RESULTS ---"
    )

    for result in results:
        print(
            f"\n{result['id']}"
        )

        print(
            f"answer_ok: "
            f"{result['answer_ok']}"
        )

        print(
            f"tool_ok: "
            f"{result['tool_ok']}"
        )

        print(
            f"args_ok: "
            f"{result['args_ok']}"
        )

        print(
            f"trajectory_ok: "
            f"{result['trajectory_ok']}"
        )

        print(
            f"actual_trajectory: "
            f"{result['actual_trajectory']}"
        )

        print(
            f"extra_tool_calls: "
            f"{result['extra_tool_calls']}"
        )

        print(
            f"judge_score: "
            f"{result['judge_score']}"
        )

        print(
            f"judge_passed: "
            f"{result['judge_passed']}"
        )

        print(
            f"judge_reason: "
            f"{result['judge_reason']}"
        )

        print(
            f"task_success: "
            f"{result['task_success']}"
        )

    summary = calculate_summary(
        results
    )

    print(
        "\n--- SUMMARY ---"
    )

    print(
        "Answer accuracy: "
        f"{summary['answer_accuracy']:.1%}"
    )

    print(
        "Tool selection accuracy: "
        f"{summary['tool_selection_accuracy']:.1%}"
    )

    print(
        "Tool argument accuracy: "
        f"{summary['tool_argument_accuracy']:.1%}"
    )

    print(
        "Trajectory accuracy: "
        f"{summary['trajectory_accuracy']:.1%}"
    )

    print(
        "Average extra tool calls: "
        f"{summary['average_extra_tool_calls']:.2f}"
    )

    print(
        "Average judge score: "
        f"{summary['average_judge_score']:.2f} / 5"
    )

    print(
        "Judge pass rate: "
        f"{summary['judge_pass_rate']:.1%}"
    )

    print(
        "Task success rate: "
        f"{summary['task_success_rate']:.1%}"
    )

    output_path = save_results(
        results,
        summary,
    )

    print(
        f"\nResults saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()