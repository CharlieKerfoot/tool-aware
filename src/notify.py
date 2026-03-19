"""Format and send the weekly digest email."""

import os
import smtplib
from datetime import date
from email.message import EmailMessage


REPO = "charliekerfoot/tool-aware"


def _snooze_url(name: str, url: str, weeks: int = 2) -> str:
    """Build a GitHub workflow_dispatch URL for snoozing a tool."""
    base = f"https://github.com/{REPO}/actions/workflows/snooze_tool.yml"
    return base


def _format_section(title: str, tools: list[dict]) -> str:
    """Format a section of the digest."""
    if not tools:
        return ""
    lines = [f"{title}"]
    for i, t in enumerate(tools, 1):
        score = t.get("total", "?")
        desc = t.get("one_liner") or t.get("description", "")
        snooze = _snooze_url(t["name"], t["url"])
        lines.append(f"  {i}. {t['name']} — {desc} — {score}/15")
        lines.append(f"     {t['url']}")
        lines.append(f"     [snooze 2w] {snooze}")
    return "\n".join(lines)


def format_digest(try_tools: list[dict], watch_tools: list[dict],
                  snoozed: list[dict]) -> str:
    """Build the full plain-text email body."""
    header = f"Tool Aware — Week of {date.today().isoformat()}\n"
    sections = [
        header,
        _format_section("TRY THIS WEEK (score 11+)", try_tools),
        _format_section("WATCH (score 8-10)", watch_tools),
    ]
    if snoozed:
        lines = ["NOW RELEVANT (snoozed items due this week)"]
        for s in snoozed:
            lines.append(f"  - {s['name']} — {s['url']}")
        sections.append("\n".join(lines))
    return "\n\n".join(s for s in sections if s)


def send_email(subject: str, body: str) -> None:
    """Send email via Gmail SMTP."""
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ["GMAIL_TO"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    print(f"[notify] Email sent to {to}")
