"""Format and send the weekly digest email."""

import os
import smtplib
from datetime import date
from email.message import EmailMessage


REPO = "charliekerfoot/tool-aware"

DIMENSIONS = ["novelty", "usefulness", "dx", "buzz", "timing"]
DIM_LABELS = {
    "novelty": "Novelty",
    "usefulness": "Usefulness",
    "dx": "Dev Experience",
    "buzz": "Buzz",
    "timing": "Timing",
}


def _snooze_url(name: str, url: str, weeks: int = 2) -> str:
    """Build a GitHub workflow_dispatch URL for snoozing a tool."""
    base = f"https://github.com/{REPO}/actions/workflows/snooze_tool.yml"
    return base


def _score_bar(value: int, max_val: int = 5) -> str:
    """Render a visual score bar as HTML."""
    pct = int((value / max_val) * 100)
    if pct >= 80:
        color = "#22c55e"
    elif pct >= 60:
        color = "#eab308"
    else:
        color = "#94a3b8"
    return (
        f'<div style="display:inline-block;width:60px;height:8px;'
        f'background:#e2e8f0;border-radius:4px;vertical-align:middle;">'
        f'<div style="width:{pct}%;height:100%;background:{color};'
        f'border-radius:4px;"></div></div>'
        f' <span style="font-size:12px;color:#64748b;">{value}/{max_val}</span>'
    )


def _tier_badge(tier: str) -> str:
    """Render a colored tier badge."""
    styles = {
        "try": ("background:#dcfce7;color:#166534;border:1px solid #bbf7d0;",
                "TRY IT"),
        "watch": ("background:#fef9c3;color:#854d0e;border:1px solid #fde68a;",
                  "WATCH"),
    }
    style, label = styles.get(tier, ("background:#f1f5f9;color:#475569;", tier.upper()))
    return (
        f'<span style="{style}font-size:11px;font-weight:700;'
        f'padding:3px 10px;border-radius:12px;letter-spacing:0.5px;">'
        f'{label}</span>'
    )


def _tool_card(tool: dict) -> str:
    """Render a single tool as an HTML card."""
    tier = tool.get("tier", "watch")
    total = tool.get("total", "?")
    desc = tool.get("one_liner") or tool.get("description", "")
    hot_take = tool.get("hot_take", "")
    snooze = _snooze_url(tool["name"], tool["url"])

    scores_html = ""
    for dim in DIMENSIONS:
        val = tool.get(dim, 0)
        label = DIM_LABELS[dim]
        scores_html += (
            f'<tr>'
            f'<td style="padding:2px 8px 2px 0;font-size:12px;color:#64748b;'
            f'white-space:nowrap;">{label}</td>'
            f'<td style="padding:2px 0;">{_score_bar(val)}</td>'
            f'</tr>'
        )

    return f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;
                padding:20px 24px;margin-bottom:16px;">
      <div style="margin-bottom:8px;">
        {_tier_badge(tier)}
        <span style="float:right;font-size:20px;font-weight:700;color:#0f172a;">
          {total}<span style="font-size:13px;font-weight:400;color:#94a3b8;">/25</span>
        </span>
      </div>
      <h2 style="margin:8px 0 4px;font-size:18px;">
        <a href="{tool['url']}" style="color:#0f172a;text-decoration:none;">
          {tool['name']}</a>
      </h2>
      <p style="margin:0 0 12px;font-size:14px;color:#475569;line-height:1.5;">
        {desc}
      </p>
      <table style="border-collapse:collapse;margin-bottom:12px;">
        {scores_html}
      </table>
      {"<p style='margin:0 0 12px;font-size:13px;color:#334155;font-style:italic;"
       "line-height:1.4;border-left:3px solid #e2e8f0;padding-left:10px;'>"
       + hot_take + "</p>" if hot_take else ""}
      <div style="font-size:12px;">
        <a href="{tool['url']}" style="color:#3b82f6;text-decoration:none;
           margin-right:16px;">View &rarr;</a>
        <a href="{snooze}" style="color:#94a3b8;text-decoration:none;">
          Snooze 2w</a>
      </div>
    </div>"""


def _section(title: str, subtitle: str, tools: list[dict]) -> str:
    """Render a section with title and tool cards."""
    if not tools:
        return ""
    cards = "\n".join(_tool_card(t) for t in tools)
    return f"""
    <div style="margin-bottom:32px;">
      <h3 style="margin:0 0 4px;font-size:14px;font-weight:700;color:#0f172a;
                 text-transform:uppercase;letter-spacing:1px;">{title}</h3>
      <p style="margin:0 0 16px;font-size:13px;color:#94a3b8;">{subtitle}</p>
      {cards}
    </div>"""


def format_digest(try_tools: list[dict], watch_tools: list[dict],
                  snoozed: list[dict]) -> str:
    """Build the full HTML email body."""
    today = date.today().isoformat()
    total_count = len(try_tools) + len(watch_tools)

    snoozed_section = ""
    if snoozed:
        items = "".join(
            f'<li style="margin-bottom:6px;font-size:14px;">'
            f'<a href="{s["url"]}" style="color:#3b82f6;text-decoration:none;">'
            f'{s["name"]}</a></li>'
            for s in snoozed
        )
        snoozed_section = f"""
        <div style="margin-bottom:32px;">
          <h3 style="margin:0 0 4px;font-size:14px;font-weight:700;color:#0f172a;
                     text-transform:uppercase;letter-spacing:1px;">
            Now Relevant</h3>
          <p style="margin:0 0 12px;font-size:13px;color:#94a3b8;">
            Previously snoozed tools that are due for another look</p>
          <ul style="margin:0;padding-left:20px;color:#334155;">{items}</ul>
        </div>"""

    return f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,
             BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="max-width:560px;margin:0 auto;padding:32px 16px;">

    <div style="text-align:center;margin-bottom:32px;">
      <h1 style="margin:0 0 4px;font-size:24px;font-weight:800;color:#0f172a;
                 letter-spacing:-0.5px;">Tool Aware</h1>
      <p style="margin:0;font-size:13px;color:#94a3b8;">
        Week of {today} &middot; {total_count} tools scored</p>
    </div>

    <div style="background:#f1f5f9;border-radius:8px;padding:12px 16px;
                margin-bottom:28px;text-align:center;">
      <span style="font-size:12px;color:#64748b;">
        Scored on
        <strong>Novelty</strong> &middot;
        <strong>Usefulness</strong> &middot;
        <strong>Dev Experience</strong> &middot;
        <strong>Buzz</strong> &middot;
        <strong>Timing</strong>
        &nbsp;(each 1-5, max 25)
      </span>
    </div>

    {_section("Try This Week", "High-signal tools worth your time right now", try_tools)}
    {_section("On the Radar", "Interesting but not urgent — keep an eye on these", watch_tools)}
    {snoozed_section}

    <div style="text-align:center;padding:20px 0;border-top:1px solid #e2e8f0;">
      <p style="margin:0;font-size:11px;color:#94a3b8;">
        Tool Aware scans Hacker News and GitHub weekly so you don't have to.<br>
        <a href="https://github.com/{REPO}" style="color:#94a3b8;">GitHub</a>
      </p>
    </div>

  </div>
</body>
</html>"""


def send_email(subject: str, body: str) -> None:
    """Send email via Gmail SMTP."""
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ["GMAIL_TO"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content("View this email in an HTML-capable client.")
    msg.add_alternative(body, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    print(f"[notify] Email sent to {to}")
