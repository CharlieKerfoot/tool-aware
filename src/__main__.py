"""Entry point: fetch → score → notify."""

from datetime import date
from src.fetch import fetch_all
from src.score import score_tools
from src.snooze import get_due
from src.notify import format_digest, send_email


def main() -> None:
    print("[main] Fetching tools...")
    tools = fetch_all()
    print(f"[main] Found {len(tools)} tools")

    print("[main] Scoring with Claude...")
    scored = score_tools(tools)
    print(f"[main] {len(scored)} tools scored")

    try_tools = [t for t in scored if t.get("tier") == "try"]
    watch_tools = [t for t in scored if t.get("tier") == "watch"]

    snoozed = get_due()
    if snoozed:
        print(f"[main] {len(snoozed)} snoozed items now due")

    body = format_digest(try_tools, watch_tools, snoozed)
    subject = f"Tool Aware — Week of {date.today().isoformat()}"

    send_email(subject, body)
    print("[main] Done!")


if __name__ == "__main__":
    main()
