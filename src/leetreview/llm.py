from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI, RateLimitError


ANALYSIS_INSTRUCTIONS = """You are a patient algorithms tutor helping a student
who has just finished their first year of university. Analyze the submitted
LeetCode solution to help the student review their thinking, not merely obtain
an accepted answer.

Write concise, friendly Chinese. Do not assume that every submission is wrong.
Do not invent test results. Use exactly these Markdown headings:

## 代码结论
## 当前思路
## 问题与思维误区
## 更好的思路
## 复杂度分析
## 知识点卡片
## 下次提醒
"""


def build_analysis_input(
    problem_id: str,
    title: str,
    description: str,
    code: str,
    language: str,
) -> str:
    return f"""题号：{problem_id}
题名：{title}
编程语言：{language}

题目描述：
<problem_description>
{description.strip()}
</problem_description>

学生代码：
<candidate_code>
{code.rstrip()}
</candidate_code>
"""


def _load_client_and_model() -> tuple[OpenAI, str]:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "replace_with_your_real_api_key":
        raise RuntimeError("OPENAI_API_KEY is missing from the .env file.")

    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    return OpenAI(api_key=api_key), model


def analyze_solution(
    problem_id: str,
    title: str,
    description: str,
    code: str,
    language: str,
) -> str:
    client, model = _load_client_and_model()
    analysis_input = build_analysis_input(
        problem_id=problem_id,
        title=title,
        description=description,
        code=code,
        language=language,
    )

    try:
        response = client.responses.create(
            model=model,
            instructions=ANALYSIS_INSTRUCTIONS,
            input=analysis_input,
            max_output_tokens=1200,
        )
    except AuthenticationError as error:
        raise RuntimeError("The OpenAI API key is invalid.") from error
    except RateLimitError as error:
        raise RuntimeError(
            "The OpenAI account has no available API quota. Check billing and usage."
        ) from error

    return response.output_text


def check_api_connection() -> str:
    client, model = _load_client_and_model()
    try:
        response = client.responses.create(
            model=model,
            input="Reply with exactly: LeetReview API connection successful",
            max_output_tokens=30,
        )
    except AuthenticationError as error:
        raise RuntimeError("The OpenAI API key is invalid.") from error
    except RateLimitError as error:
        raise RuntimeError(
            "The OpenAI account has no available API quota. Check billing and usage."
        ) from error

    return response.output_text
