import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv(override=True)


judge_llm = ChatOpenAI(
    model=os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6",
    ),
    temperature=0,
    reasoning_effort="none",
)


JUDGE_PROMPT = """
You are evaluating the quality of an AI agent answer.

Evaluate whether the actual answer correctly satisfies
the user's question and is consistent with the expected answer.

Use this scale:

1 = completely incorrect
2 = mostly incorrect
3 = partially correct
4 = correct
5 = fully correct and clear

Return ONLY valid JSON using this exact structure:

{{
  "score": 1,
  "passed": false,
  "reason": "short explanation"
}}

A score of 4 or 5 means passed.

Question:
{question}

Expected answer:
{expected_answer}

Actual answer:
{actual_answer}
"""


def evaluate_with_llm_judge(
    question: str,
    expected_answer: str,
    actual_answer: str,
) -> dict:
    prompt = JUDGE_PROMPT.format(
        question=question,
        expected_answer=expected_answer,
        actual_answer=actual_answer,
    )

    response = judge_llm.invoke(
        prompt
    )

    content = response.content.strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "score": 0,
            "passed": False,
            "reason":
                "Judge returned invalid JSON.",
        }

    return {
        "score":
            result.get("score", 0),

        "passed":
            result.get("passed", False),

        "reason":
            result.get(
                "reason",
                "",
            ),
    }