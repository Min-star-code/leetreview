from __future__ import annotations

import argparse
from pathlib import Path

from leetreview.llm import analyze_solution, check_api_connection
from leetreview.notebook import ReviewCard, save_review_card


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="leetreview",
        description="Generate Markdown review cards for LeetCode practice.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "check-api",
        help="Send a small request to verify the OpenAI API connection.",
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a solution with an LLM and print the review.",
    )
    analyze_parser.add_argument("--problem-id", required=True)
    analyze_parser.add_argument("--title", required=True)
    analyze_parser.add_argument("--description-file", required=True, type=Path)
    analyze_parser.add_argument("--code-file", required=True, type=Path)
    analyze_parser.add_argument("--language", default="python")
    analyze_parser.add_argument(
        "--output-dir",
        default=Path("notebook"),
        type=Path,
        help="Directory for the generated AI review card.",
    )

    new_parser = subparsers.add_parser("new", help="Create a new review card.")
    new_parser.add_argument("--problem-id", required=True, help="LeetCode problem id.")
    new_parser.add_argument("--title", required=True, help="Problem title.")
    new_parser.add_argument(
        "--code-file",
        required=True,
        type=Path,
        help="Path to your attempted solution code.",
    )
    new_parser.add_argument(
        "--language",
        default="python",
        help="Programming language used by the submitted code.",
    )
    new_parser.add_argument(
        "--mistake",
        default="",
        help="What went wrong in your attempt.",
    )
    new_parser.add_argument(
        "--better-approach",
        default="",
        help="A better idea or solution direction.",
    )
    new_parser.add_argument(
        "--knowledge",
        default="",
        help="Comma-separated knowledge points.",
    )
    new_parser.add_argument(
        "--output-dir",
        default=Path("notebook"),
        type=Path,
        help="Directory for generated Markdown cards.",
    )

    return parser


def handle_new(args: argparse.Namespace) -> Path:
    code = args.code_file.read_text(encoding="utf-8")
    knowledge_points = [
        item.strip() for item in args.knowledge.split(",") if item.strip()
    ]

    card = ReviewCard(
        problem_id=args.problem_id,
        title=args.title,
        code=code,
        language=args.language,
        mistake=args.mistake,
        better_approach=args.better_approach,
        knowledge_points=knowledge_points,
    )
    return save_review_card(card, args.output_dir)


def handle_analyze(args: argparse.Namespace) -> Path:
    description = args.description_file.read_text(encoding="utf-8")
    code = args.code_file.read_text(encoding="utf-8")
    analysis = analyze_solution(
        problem_id=args.problem_id,
        title=args.title,
        description=description,
        code=code,
        language=args.language,
    )
    card = ReviewCard(
        problem_id=args.problem_id,
        title=args.title,
        code=code,
        language=args.language,
        analysis=analysis,
    )
    return save_review_card(card, args.output_dir)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "new":
        output_path = handle_new(args)
        print(f"Saved review card: {output_path}")
    elif args.command == "check-api":
        try:
            print(check_api_connection())
        except RuntimeError as error:
            parser.exit(status=1, message=f"API check failed: {error}\n")
    elif args.command == "analyze":
        try:
            output_path = handle_analyze(args)
            print(f"Saved AI review card: {output_path}")
        except RuntimeError as error:
            parser.exit(status=1, message=f"Analysis failed: {error}\n")


if __name__ == "__main__":
    main()
