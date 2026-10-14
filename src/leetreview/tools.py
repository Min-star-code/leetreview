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
