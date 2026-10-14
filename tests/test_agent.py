from types import SimpleNamespace

from leetreview.agent import call_tool, run_agent
from leetreview.cli import build_parser


def tool_call(name, arguments="{}", call_id="call_1"):
    return SimpleNamespace(
        type="function_call", name=name, arguments=arguments, call_id=call_id
    )


def tool_call_response(*calls):
    return SimpleNamespace(output=list(calls), output_text="")


def final_response(text):
    message = SimpleNamespace(type="message")
    return SimpleNamespace(output=[message], output_text=text)


class FakeResponses:
    def __init__(self, responses):
        self.responses = list(responses)
        self.inputs = []

    def create(self, **kwargs):
        # Copy the conversation, because the agent keeps adding to its list.
        self.inputs.append(list(kwargs["input"]))
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


class FakeClient:
    def __init__(self, responses):
        self.responses = FakeResponses(responses)


def tool_outputs(conversation):
    return [
        item["output"]
        for item in conversation
        if isinstance(item, dict) and item.get("type") == "function_call_output"
    ]


def test_agent_returns_final_review_after_tool_call():
    client = FakeClient(
        [tool_call_response(tool_call("run_tests")), final_response("## Verdict")]
    )
    tools = {"run_tests": lambda: {"passed": [], "failed": []}}

    result = run_agent(client, "fake-model", "Review this.", tools)

    assert result.finished
    assert result.review == "## Verdict"
    assert result.turns == 2
    assert result.tool_calls == ["run_tests"]
    assert tool_outputs(client.responses.inputs[1]) == [
        '{"passed": [], "failed": []}'
    ]


def test_agent_finishes_in_one_turn_without_tool_calls():
    client = FakeClient([final_response("## Verdict")])

    result = run_agent(client, "fake-model", "Review this.", {})

    assert result.finished
    assert result.turns == 1
    assert result.tool_calls == []


def test_agent_stops_at_max_turns():
    client = FakeClient([tool_call_response(tool_call("run_tests"))])
    tools = {"run_tests": lambda: {"passed": [], "failed": []}}

    result = run_agent(client, "fake-model", "Review this.", tools, max_turns=3)

    assert not result.finished
    assert result.review == ""
    assert result.turns == 3
    assert len(client.responses.inputs) == 3
    assert result.tool_calls == ["run_tests"] * 3


def test_agent_sends_tool_error_back_to_model():
    def broken_tool():
        raise FileNotFoundError("tests.json not found")

    client = FakeClient(
        [tool_call_response(tool_call("run_tests")), final_response("## Verdict")]
    )

    result = run_agent(client, "fake-model", "Review this.", {"run_tests": broken_tool})

    assert result.finished
    assert tool_outputs(client.responses.inputs[1]) == [
        "Error: FileNotFoundError: tests.json not found"
    ]


def test_call_tool_passes_arguments_to_tool():
    tools = {"search_notebook": lambda keyword: [keyword]}

    assert call_tool(tools, "search_notebook", '{"keyword": "dp"}') == '["dp"]'


def test_call_tool_reports_unknown_tool():
    assert call_tool({}, "delete_everything", "{}").startswith("Error: KeyError")


def test_call_tool_reports_invalid_arguments():
    tools = {"run_tests": lambda: {}}

    assert call_tool(tools, "run_tests", "not json").startswith("Error:")


def test_review_command_is_available():
    args = build_parser().parse_args(
        [
            "review",
            "--problem-id", "1",
            "--title", "Two Sum",
            "--description-file", "examples/two_sum.md",
            "--code-file", "examples/two_sum_buggy.py",
            "--tests-file", "examples/two_sum_tests.json",
        ]
    )

    assert args.command == "review"
    assert str(args.output_dir) == "notebook"
