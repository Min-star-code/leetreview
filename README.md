# LeetReview

LeetReview is a Python CLI that turns LeetCode attempts into personalized Markdown review cards with help from an LLM.

Given a problem description and a student's solution, LeetReview analyzes the approach, identifies possible misconceptions, explains complexity, extracts reusable concepts, and saves the result as a local mistake notebook entry.

## Features

- Reads the problem id, title, description, and solution file
- Supports solutions written in C, Python, and other languages
- Uses the OpenAI Responses API to generate an English review
- Handles correct solutions without inventing mistakes
- Generates structured Markdown review cards
- Records creation and next-review dates
- Includes a `review` agent that runs the solution on real test cases and
  searches earlier review cards before it writes the review
- Includes a manual mode that does not call an LLM
- Includes a focused pytest test suite

## Workflow

```text
Problem description + student solution
                   |
                   v
          LeetReview builds a prompt
                   |
                   v
         OpenAI API returns a review
                   |
                   v
         A Markdown card is generated
                   |
                   v
             Saved to notebook/
```

## Requirements

- Python 3.10 or newer
- An OpenAI API key
- Network access to the OpenAI API

## Installation

Clone the repository, enter the project directory, and run:

```bash
python3 -m pip install -e ".[dev]"
```

The `-e` flag installs the package in editable mode, so source changes are available without reinstalling it.

## API Configuration

1. Create a key on the [OpenAI API Keys](https://platform.openai.com/api-keys) page.
2. Copy `.env.example` to a new file named `.env`.
3. Add your real key to `.env`:

```dotenv
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-5.4-mini
```

Never place a real API key in source code or commit `.env`. The project already excludes `.env` through `.gitignore`.

Verify the API connection:

```bash
python3 -m leetreview.cli check-api
```

A successful check prints:

```text
LeetReview API connection successful
```

## Analyze a Solution

The repository includes a C solution and a short description for LeetCode 21:

```bash
python3 -m leetreview.cli analyze \
  --problem-id 21 \
  --title "Merge Two Sorted Lists" \
  --description-file examples/merge_two_sorted_lists.md \
  --code-file examples/merge_two_sorted_lists.c \
  --language c
```

The generated card is saved to:

```text
notebook/21-merge-two-sorted-lists.md
```

The `notebook/` directory is excluded from Git by default so users can keep personal review notes private. See the [public sample review](examples/sample_review.md) for an example output.

## Agent Review

`analyze` sends one request: the LLM only reads the code, so it cannot know
whether the code really works. `review` is an agent. The LLM is given three
tools and decides for itself which ones to call, in a loop, until it has enough
evidence to write the review.

### Agent Flow

```text
Problem description + Python solution + test cases (JSON)
                   |
                   v
   +--> Send the conversation and the tool descriptions to the LLM
   |               |
   |               v
   |     Did the LLM ask for a tool?
   |        |                 |
   |       yes                no --> final review --> saved to notebook/
   |        |
   |        v
   |   Run the Python function for that tool.
   |   Add its result (or its error message) to the conversation.
   |        |
   +--------+        (at most 6 turns, then stop without saving a card)
```

- **Tool calling**: each tool is a plain Python function in `tools.py`, with a
  description that the LLM reads.
- **Loop**: `run_agent` in `agent.py` is a single `for` loop. One turn is one
  request to the LLM.
- **The LLM decides the next step**: the code never says "run the tests, then
  search". Each turn, the LLM's reply decides whether a tool runs or the loop
  ends.
- **Turn limit**: `MAX_TURNS = 6`. If the LLM is still asking for tools after
  six turns, the command stops, prints the reason and the tools that were
  called, and does not save a card.
- **Tool errors**: if a tool raises an exception, the loop does not crash. The
  error message is sent back to the LLM as the tool result.

### Tools

| Tool | What it does |
| --- | --- |
| `run_tests` | Runs the Python solution on each test case in a separate process with a 5-second timeout per case, and returns the passed and failed cases |
| `search_notebook` | Searches the existing cards in `notebook/` for a keyword and returns matching card names and lines |
| `read_card` | Returns the full text of one earlier card |

The LLM cannot choose file paths. The solution file and the test file are fixed
by the command line, and `read_card` only accepts a file name inside the
notebook directory.

### `analyze` vs. `review`

| | `analyze` | `review` |
| --- | --- | --- |
| LLM requests | Exactly one | One per turn, up to 6 |
| Knows if the code works | No, it only reads the code | Yes, from `run_tests` results |
| Uses earlier cards | No | Yes, through `search_notebook` and `read_card` |
| Languages | Any | Python only |
| Needs test cases | No | Yes, a JSON file |

### Run the Agent

The repository includes a Two Sum solution with a real bug (it can use the same
element twice) and four test cases:

```bash
python3 -m leetreview.cli review \
  --problem-id 1 \
  --title "Two Sum" \
  --description-file examples/two_sum.md \
  --code-file examples/two_sum_buggy.py \
  --tests-file examples/two_sum_tests.json
```

A test file names the method of `Solution` to call and lists the cases:

```json
{
  "method": "twoSum",
  "cases": [
    {"args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
    {"args": [[3, 2, 4], 6], "expected": [1, 2]}
  ]
}
```

On the included example, `run_tests` returns this result to the LLM (cases 2
and 3 fail because the same index is used twice):

```json
{
  "passed": [
    {"case": 1, "args": [[2, 7, 11, 15], 9], "expected": [0, 1], "actual": [0, 1]},
    {"case": 4, "args": [[-1, -2, -3, -4, -5], -8], "expected": [2, 4], "actual": [2, 4]}
  ],
  "failed": [
    {"case": 2, "args": [[3, 2, 4], 6], "expected": [1, 2], "actual": [0, 0]},
    {"case": 3, "args": [[3, 3], 6], "expected": [0, 1], "actual": [0, 0]}
  ]
}
```

### Example Trace (Illustrative)

This trace shows how one run could go on the included example. It is written by
hand to explain the loop and is not a recording of a real run. Only the
`run_tests` result above is real output. Because the LLM chooses the tools, the
order and the number of turns can differ from run to run.

```text
Turn 1  LLM asks for: run_tests
        Tool result:  2 passed, 2 failed (cases 2 and 3 return [0, 0])
Turn 2  LLM asks for: search_notebook(keyword="two sum")
        Tool result:  [] (no earlier cards yet)
Turn 3  LLM writes the final review; the loop ends and the card is saved
```

### Limitations

- `run_tests` runs the solution on your own machine. The separate process and
  the timeout protect against crashes and infinite loops, but this is not a
  security sandbox. Only run code that you trust.
- Outputs are compared with `==`, so `[1, 0]` does not match an expected
  `[0, 1]`.
- Only solutions written as a LeetCode-style `class Solution` are supported.

## Manual Mode

To create a card without calling an LLM, provide the review fields yourself:

```bash
python3 -m leetreview.cli new \
  --problem-id 1 \
  --title "Two Sum" \
  --code-file examples/two_sum_wrong.py \
  --language python \
  --mistake "Used a nested-loop brute-force approach" \
  --better-approach "Store previously visited values in a hash map" \
  --knowledge "hash map, complement search, time complexity"
```

## Tests

```bash
python3 -m pytest
```

## Project Structure

```text
.
|-- examples/               # Sample problems, solutions, and output
|-- src/leetreview/
|   |-- agent.py            # Agent loop for the review command
|   |-- cli.py              # Command-line entry point
|   |-- llm.py              # Prompt construction and OpenAI API calls
|   |-- notebook.py         # Markdown card generation
|   `-- tools.py            # Tools the agent can call
|-- tests/                  # Automated tests
|-- .env.example            # Safe API configuration template
|-- .gitignore              # Git ignore rules
|-- pyproject.toml          # Python package configuration
`-- README.md
```

## Project Status

LeetReview is currently an MVP. The complete path from code input to LLM analysis and local Markdown output is working, and the `review` agent can test Python solutions and consult earlier cards.

Planned improvements:

- Use structured outputs for more reliable analysis fields
- Add a friendlier interactive input flow
- Add completion tracking for reviews
- Build a small web interface

## Security and Cost

- API requests may incur charges. Configure an appropriate usage limit on the OpenAI Platform.
- Never publish `.env`, API keys, or other credentials.
- Run `git status` before committing and confirm that `.env` is not staged.

## License

This project is available under the [MIT License](LICENSE).
