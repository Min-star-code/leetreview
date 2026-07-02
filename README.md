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
|   |-- cli.py              # Command-line entry point
|   |-- llm.py              # Prompt construction and OpenAI API calls
|   `-- notebook.py         # Markdown card generation
|-- tests/                  # Automated tests
|-- .env.example            # Safe API configuration template
|-- .gitignore              # Git ignore rules
|-- pyproject.toml          # Python package configuration
`-- README.md
```

## Project Status

LeetReview is currently an MVP. The complete path from code input to LLM analysis and local Markdown output is working.

Planned improvements:

- Use structured outputs for more reliable analysis fields
- Add a friendlier interactive input flow
- Add review search and completion tracking
- Build a small web interface

## Security and Cost

- API requests may incur charges. Configure an appropriate usage limit on the OpenAI Platform.
- Never publish `.env`, API keys, or other credentials.
- Run `git status` before committing and confirm that `.env` is not staged.

## License

This project is available under the [MIT License](LICENSE).
