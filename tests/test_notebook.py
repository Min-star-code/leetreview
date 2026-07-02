from leetreview.notebook import ReviewCard, build_filename, render_markdown


def test_build_filename_normalizes_title():
    card = ReviewCard(problem_id="1", title="Two Sum", code="print('hi')")

    assert build_filename(card) == "1-two-sum.md"


def test_render_markdown_includes_core_sections():
    card = ReviewCard(
        problem_id="1",
        title="Two Sum",
        code="return []",
        mistake="Brute force only.",
        better_approach="Use a hash map.",
        knowledge_points=["hash map", "time complexity"],
    )

    markdown = render_markdown(card)

    assert "# 1. Two Sum" in markdown
    assert "Brute force only." in markdown
    assert "- hash map" in markdown
    assert "```python" in markdown


def test_render_markdown_uses_selected_language():
    card = ReviewCard(
        problem_id="21",
        title="Merge Two Sorted Lists",
        code="struct ListNode* mergeTwoLists(void) {}",
        language="c",
    )

    markdown = render_markdown(card)

    assert "```c" in markdown


def test_render_markdown_includes_ai_analysis():
    card = ReviewCard(
        problem_id="21",
        title="Merge Two Sorted Lists",
        code="return dummy.next;",
        language="c",
        analysis="## 代码结论\n\n代码正确。",
    )

    markdown = render_markdown(card)

    assert "## AI Review" in markdown
    assert "## 代码结论" in markdown
    assert "代码正确。" in markdown
    assert "## Mistake" not in markdown
