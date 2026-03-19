# tool-aware

Weekly automated digest that discovers emerging dev tools from Hacker News and GitHub, scores them with Claude, and emails the results.

## How it works

1. **Fetch** — Pulls new "Show HN" posts and trending GitHub repos matching AI/dev-tool topics from the past week
2. **Score** — Sends the list to Claude (Sonnet) which scores each tool on Signal (traction), Fit (relevance to agentic AI / dev tools), and Timing (novelty). Each dimension is 1-5, max 15.
3. **Notify** — Emails a plain-text digest with two tiers:
   - **TRY THIS WEEK** (score 11+)
   - **WATCH** (score 8-10)
4. **Snooze** — Each tool includes a snooze link (GitHub workflow dispatch). Snoozed tools reappear in a "NOW RELEVANT" section when their surface date arrives.

## Setup

### 1. Add GitHub secrets

In your repo: Settings → Secrets and variables → Actions, add:

| Secret | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key |
| `GMAIL_USER` | Gmail address to send from |
| `GMAIL_APP_PASSWORD` | [Gmail App Password](https://support.google.com/accounts/answer/185833) |
| `GMAIL_TO` | Recipient email address |

### 2. Push to GitHub

The workflow runs automatically every Sunday at 8am UTC. You can also trigger it manually from the Actions tab.

## Local development

```bash
uv sync
ANTHROPIC_API_KEY=... GMAIL_USER=... GMAIL_APP_PASSWORD=... GMAIL_TO=... uv run python -m src
```

### Snooze a tool manually

```bash
uv run python -m src.snooze --add "tool-name" "https://github.com/..." 2
```

## Project structure

```
src/
  fetch.py      # HN Algolia + GitHub Search APIs
  score.py      # Claude scoring with rubric
  snooze.py     # Snooze management (read/write data/snooze.json)
  notify.py     # Email formatting + Gmail SMTP
  __main__.py   # Orchestrator
data/
  snooze.json   # Snoozed tools (auto-committed by actions)
.github/workflows/
  weekly.yml        # Sunday cron + manual trigger
  snooze_tool.yml   # One-click snooze via workflow dispatch
```
