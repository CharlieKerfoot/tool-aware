"""Score tools using Claude API."""

import json
import os
import anthropic


RUBRIC_PROMPT = """\
You are evaluating emerging developer tools for a weekly digest.

Score each tool on five dimensions (1-5 each):
- Novelty: How original is this? 5 = first-of-its-kind approach, 1 = yet-another clone
- Usefulness: Would this actually save a developer time or solve a real pain point? \
5 = obvious daily-driver potential, 1 = solution looking for a problem
- Developer Experience: Polish, docs quality, ease of getting started. \
5 = npm install and go, 1 = undocumented and broken
- Buzz: GitHub stars velocity, HN points, community excitement in its first week. \
5 = trending everywhere, 1 = crickets
- Timing: Is the ecosystem ready for this? 5 = perfect moment, 1 = too early or too late

Return a JSON array of objects with these fields:
  name, url, novelty, usefulness, dx, buzz, timing, total, tier, one_liner, hot_take

Where:
  total = novelty + usefulness + dx + buzz + timing
  tier = "try" if total >= 18, "watch" if total >= 13, "drop" if total < 13
  one_liner = a single sentence describing what the tool does
  hot_take = a brief, opinionated 1-2 sentence take on why this matters or doesn't

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
        max_tokens=4096,
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
