from __future__ import annotations

from dataclasses import dataclass
import json

from leetreview.tools import TOOL_SCHEMAS


MAX_TURNS = 6

REVIEW_INSTRUCTIONS = """You are a patient algorithms tutor helping a student
who has just finished their first year of university. Review the submitted
LeetCode solution to help the student review their thinking, not merely obtain
an accepted answer.

You have tools. Use run_tests to find out whether the solution really works
before you judge it. Use search_notebook and read_card to check whether the
student has made a related mistake before. You decide which tools to call and
when you have enough evidence to stop.

Write concise, friendly English. Do not assume that every submission is wrong.
Never invent test results or past cards: only report what the tools returned.
When you are ready, reply with the final review using exactly these Markdown
headings:

## Verdict
## Test Results
## Current Approach
## Issues and Misconceptions
## Related Past Mistakes
## Improved Approach
## Complexity Analysis
## Next-Time Reminder
"""


@dataclass(frozen=True)
class AgentResult:
    review: str
    turns: int
    tool_calls: list[str]
    finished: bool


def run_agent(
    client,
    model: str,
    review_input: str,
    tools: dict,
    max_turns: int = MAX_TURNS,
) -> AgentResult:
    conversation = [{"role": "user", "content": review_input}]
    tool_calls = []

    for turn in range(1, max_turns + 1):
        response = client.responses.create(
            model=model,
            instructions=REVIEW_INSTRUCTIONS,
            input=conversation,
            tools=TOOL_SCHEMAS,
        )
        # Keep everything the model said, so the next request has the history.
        conversation += response.output

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return AgentResult(response.output_text, turn, tool_calls, True)

        for call in calls:
            tool_calls.append(call.name)
            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": call_tool(tools, call.name, call.arguments),
                }
            )

    return AgentResult("", max_turns, tool_calls, False)


def call_tool(tools: dict, name: str, arguments: str) -> str:
    # A failing tool must not crash the loop. The error text goes back to the
    # LLM as the tool result, and the LLM decides what to do next.
    try:
        result = tools[name](**json.loads(arguments))
    except Exception as error:
        return f"Error: {type(error).__name__}: {error}"
    return json.dumps(result)
