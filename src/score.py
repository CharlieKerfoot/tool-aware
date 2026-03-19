"""Score tools using Claude API."""

import json
import os
import anthropic


RUBRIC_PROMPT = """\
You are evaluating emerging developer tools for a weekly digest.

Score each tool on three dimensions (1-5 each):
- Signal: GitHub stars velocity + HN traction in first week
- Fit: Relevance to agentic AI, dev tools, coding assistants, Python/TS ecosystems
- Timing: Is this genuinely new (week 1) or already mainstream?

Return a JSON array of objects with these fields:
  name, url, signal, fit, timing, total, tier, one_liner

Where:
  total = signal + fit + timing
  tier = "try" if total >= 11, "watch" if total >= 8, "drop" if total < 8
  one_liner = a single sentence describing what the tool does

Only include tools with tier "try" or "watch" in the output.

Here are the tools to evaluate:
"""


def score_tools(tools: list[dict]) -> list[dict]:
    """Send tools to Claude for scoring, return scored and filtered list."""
    if not tools:
        return []

    client = anthropic.Anthropic()
    tools_json = json.dumps(tools, indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": RUBRIC_PROMPT + tools_json,
        }],
    )

    text = message.content[0].text
    # Strip markdown fences if present
    if "```" in text:
        lines = text.split("\n")
        json_lines = []
        inside = False
        for line in lines:
            if line.strip().startswith("```"):
                inside = not inside
                continue
            if inside:
                json_lines.append(line)
        text = "\n".join(json_lines)

    scored = json.loads(text)
    scored.sort(key=lambda t: t["total"], reverse=True)
    return [t for t in scored if t.get("tier") in ("try", "watch")]
