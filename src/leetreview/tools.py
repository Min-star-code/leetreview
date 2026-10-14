from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


TEST_TIMEOUT_SECONDS = 5

# This small program runs inside the child process. It loads the student's
# file, calls one method of Solution, and prints the return value as JSON.
RUNNER_CODE = """import json, runpy, sys

namespace = runpy.run_path(sys.argv[1])
solution = namespace["Solution"]()
method = getattr(solution, sys.argv[2])
args = json.loads(sys.argv[3])
print(json.dumps(method(*args)))
"""


def run_tests(
    code_file: Path,
    tests_file: Path,
    timeout: float = TEST_TIMEOUT_SECONDS,
) -> dict:
    if code_file.suffix != ".py":
        raise ValueError("run_tests only supports Python solutions.")

    tests = json.loads(tests_file.read_text(encoding="utf-8"))
    passed = []
    failed = []

    for number, case in enumerate(tests["cases"], start=1):
        outcome = _run_case(code_file, tests["method"], case["args"], timeout)
        report = {
            "case": number,
            "args": case["args"],
            "expected": case["expected"],
            **outcome,
        }
        if "error" not in outcome and outcome["actual"] == case["expected"]:
            passed.append(report)
        else:
            failed.append(report)

    return {"passed": passed, "failed": failed}


def _run_case(code_file: Path, method: str, args: list, timeout: float) -> dict:
    command = [
        sys.executable,
        "-c",
        RUNNER_CODE,
        str(code_file),
        method,
        json.dumps(args),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"Timed out after {timeout} seconds."}

    if result.returncode != 0:
        error_lines = result.stderr.strip().splitlines()
        return {"error": error_lines[-1] if error_lines else "The solution crashed."}

    # The student's code may print debug output, so only the last line is ours.
    return {"actual": json.loads(result.stdout.strip().splitlines()[-1])}


def search_notebook(keyword: str, notebook_dir: Path) -> list[dict]:
    if not keyword.strip():
        raise ValueError("keyword must not be empty.")

    matches = []
    for card_path in sorted(notebook_dir.glob("*.md")):
        lines = card_path.read_text(encoding="utf-8").splitlines()
        matching_lines = [
            line.strip() for line in lines if keyword.lower() in line.lower()
        ]
        if matching_lines:
            matches.append({"card": card_path.name, "lines": matching_lines[:3]})
    return matches


def read_card(card_name: str, notebook_dir: Path) -> str:
    # Only plain file names are allowed, so the LLM cannot read files
    # outside the notebook with a name like "../.env".
    if Path(card_name).name != card_name or not card_name.endswith(".md"):
        raise ValueError("card_name must be a .md file name inside the notebook.")
    return (notebook_dir / card_name).read_text(encoding="utf-8")


# The descriptions below are what the LLM reads when it decides which tool
# to call. File paths are fixed by the CLI, so they are not parameters here.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "run_tests",
        "description": (
            "Run the student's Python solution on the test cases for this "
            "problem. Returns the passed cases and the failed cases, with the "
            "expected and actual output or the error for each failed case."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_notebook",
        "description": (
            "Search the student's earlier review cards for a keyword, such as "
            "a topic ('hash map') or a mistake ('off-by-one'). Returns the "
            "names of matching cards with up to three matching lines each."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Case-insensitive text to look for.",
                }
            },
            "required": ["keyword"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_card",
        "description": (
            "Read the full text of one earlier review card. Use a card name "
            "returned by search_notebook."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string",
                    "description": "File name of the card, e.g. '1-two-sum.md'.",
                }
            },
            "required": ["card_name"],
            "additionalProperties": False,
        },
    },
]


def build_tools(code_file: Path, tests_file: Path, notebook_dir: Path) -> dict:
    return {
        "run_tests": lambda: run_tests(code_file, tests_file),
        "search_notebook": lambda keyword: search_notebook(keyword, notebook_dir),
        "read_card": lambda card_name: read_card(card_name, notebook_dir),
    }
