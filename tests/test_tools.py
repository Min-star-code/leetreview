import json

import pytest

from leetreview.tools import run_tests


def write_tests_file(tmp_path, cases):
    tests_file = tmp_path / "tests.json"
    tests_file.write_text(json.dumps({"method": "double", "cases": cases}))
    return tests_file


def test_run_tests_separates_passed_and_failed_cases(tmp_path):
    code_file = tmp_path / "solution.py"
    code_file.write_text(
        "class Solution:\n"
        "    def double(self, n):\n"
        "        return n + 2\n"
    )
    tests_file = write_tests_file(
        tmp_path,
        [{"args": [2], "expected": 4}, {"args": [5], "expected": 10}],
    )

    result = run_tests(code_file, tests_file)

    assert [report["case"] for report in result["passed"]] == [1]
    assert result["failed"] == [
        {"case": 2, "args": [5], "expected": 10, "actual": 7}
    ]


def test_run_tests_reports_timeout(tmp_path):
    code_file = tmp_path / "solution.py"
    code_file.write_text(
        "class Solution:\n"
        "    def double(self, n):\n"
        "        while True:\n"
        "            pass\n"
    )
    tests_file = write_tests_file(tmp_path, [{"args": [2], "expected": 4}])

    result = run_tests(code_file, tests_file, timeout=0.5)

    assert result["passed"] == []
    assert "Timed out" in result["failed"][0]["error"]


def test_run_tests_reports_crash(tmp_path):
    code_file = tmp_path / "solution.py"
    code_file.write_text(
        "class Solution:\n"
        "    def double(self, n):\n"
        "        return n / 0\n"
    )
    tests_file = write_tests_file(tmp_path, [{"args": [2], "expected": 4}])

    result = run_tests(code_file, tests_file)

    assert "ZeroDivisionError" in result["failed"][0]["error"]


def test_run_tests_rejects_non_python_solution(tmp_path):
    code_file = tmp_path / "solution.c"
    code_file.write_text("int main(void) { return 0; }")
    tests_file = write_tests_file(tmp_path, [])

    with pytest.raises(ValueError):
        run_tests(code_file, tests_file)
