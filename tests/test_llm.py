from leetreview.llm import build_analysis_input


def test_build_analysis_input_contains_problem_and_code():
    prompt = build_analysis_input(
        problem_id="21",
        title="Merge Two Sorted Lists",
        description="Merge two sorted linked lists.",
        code="return dummy.next;",
        language="c",
    )

    assert "题号：21" in prompt
    assert "编程语言：c" in prompt
    assert "<problem_description>" in prompt
    assert "return dummy.next;" in prompt
    assert "<candidate_code>" in prompt
