"""Manage snoozed tools — defer tools to surface later."""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path


SNOOZE_FILE = Path(__file__).resolve().parent.parent / "data" / "snooze.json"


def load_snoozes() -> list[dict]:
    """Load snooze list from disk."""
    if not SNOOZE_FILE.exists():
        return []
    return json.loads(SNOOZE_FILE.read_text())


def save_snoozes(snoozes: list[dict]) -> None:
    """Write snooze list to disk."""
    SNOOZE_FILE.write_text(json.dumps(snoozes, indent=2) + "\n")


def get_due() -> list[dict]:
    """Return snoozed items that are due, removing them from the file."""
    snoozes = load_snoozes()
    today = date.today().isoformat()
    due = [s for s in snoozes if s["surface_date"] <= today]
    remaining = [s for s in snoozes if s["surface_date"] > today]
    if due:
        save_snoozes(remaining)
    return due


def add_snooze(name: str, url: str, weeks: int) -> None:
    """Add a tool to the snooze list."""
    snoozes = load_snoozes()
    surface = (date.today() + timedelta(weeks=weeks)).isoformat()
    snoozes.append({
        "name": name,
        "url": url,
        "surface_date": surface,
    })
    save_snoozes(snoozes)
    print(f"Snoozed '{name}' until {surface}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage snoozed tools")
    parser.add_argument("--add", nargs=3, metavar=("NAME", "URL", "WEEKS"),
                        help="Snooze a tool: --add 'name' 'url' 2")
    args = parser.parse_args()

    if args.add:
        name, url, weeks = args.add
        add_snooze(name, url, int(weeks))
    else:
        due = get_due()
        if due:
            for item in due:
                print(f"  Due: {item['name']} — {item['url']}")
        else:
            print("No snoozed items due.")


if __name__ == "__main__":
    main()
