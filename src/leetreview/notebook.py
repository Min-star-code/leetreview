from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
import re


@dataclass(frozen=True)
class ReviewCard:
    problem_id: str
    title: str
    code: str
    language: str = "python"
    mistake: str = ""
    better_approach: str = ""
    knowledge_points: list[str] = field(default_factory=list)
    analysis: str = ""


def save_review_card(card: ReviewCard, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / build_filename(card)
    file_path.write_text(render_markdown(card), encoding="utf-8")
    return file_path


def build_filename(card: ReviewCard) -> str:
    title_slug = re.sub(r"[^a-zA-Z0-9]+", "-", card.title.lower()).strip("-")
    return f"{card.problem_id}-{title_slug}.md"


def render_markdown(card: ReviewCard) -> str:
    created_at = date.today()
    next_review_at = created_at + timedelta(days=3)
    knowledge = "\n".join(f"- {point}" for point in card.knowledge_points)
    if not knowledge:
        knowledge = "- TODO"

    if card.analysis:
        review_content = f"## AI Review\n\n{card.analysis.strip()}"
    else:
        review_content = f"""## Mistake

{card.mistake or "TODO"}

## Better Approach

{card.better_approach or "TODO"}

## Knowledge Points

{knowledge}"""

    return f"""# {card.problem_id}. {card.title}

## Metadata

- Created: {created_at.isoformat()}
- Next review: {next_review_at.isoformat()}

## My Attempt

```{card.language}
{card.code.rstrip()}
```

{review_content}

## Reflection

- Why did I choose my original approach?
- What signal should remind me to use the better approach next time?
- Can I solve a similar problem without looking at the answer?
"""
