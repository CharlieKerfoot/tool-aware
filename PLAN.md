Project: tool-aware
Stack: GitHub Actions + Python + Claude API + Gmail SMTP

Architecture
.github/workflows/weekly.yml   # cron trigger, runs every Sunday 8am
src/
  fetch.py      # pull signals from HN + GitHub APIs
  score.py      # Claude API call → scored digest
  notify.py     # send email via Gmail SMTP
  snooze.py     # read/write snooze.json, surface due items
data/
  snooze.json   # { tool, url, reason, surface_date } — committed to repo
One file per concern. No database. snooze.json lives in the repo and gets auto-committed by the action.

Scoring Rubric (passed to Claude)
3 dimensions, 1-5 each:

Signal — GitHub stars velocity + HN traction in first week
Fit — relevance to: agentic AI, dev tools, coding assistants, Python/TS
Timing — is this week 1 or already mainstream?

Claude returns ranked JSON. Anything scoring ≥11 gets "try this week." 8-10 gets "watch." Below 8 is dropped.

Snooze Flow
Email includes a snooze link for each tool — a mailto or reply-based trigger (simplest: a hardcoded reply keyword). Easier: the email just has a section "Reply with SNOOZE [tool name] 2w" and a companion action parses your reply via Gmail API.
Actually simpler — skip the reply parsing entirely. The email contains a link to a GitHub Actions workflow_dispatch URL with pre-filled inputs. One click → triggers action → appends to snooze.json → commits. Zero infra.
Snoozed items surface in the next weekly email under a "Now Relevant" section when their surface_date is reached.

Secrets needed
ANTHROPIC_API_KEY
GMAIL_USER
GMAIL_APP_PASSWORD
GITHUB_TOKEN        # built-in, needed for committing snooze.json

Data sources

HN Algolia API — hn.algolia.com/api/v1/search filtered to Show HN + keywords, past week
GitHub Search API — api.github.com/search/repositories sorted by stars, created past week, topics: llm agent mcp claude

No API keys needed for either. Rate limits are fine for weekly cadence.

Email format
🔭 Tool Radar — Week of [date]

⚡ TRY THIS WEEK (score 11+)
  1. [tool] — [one line] — [score] — [snooze link]

👀 WATCH (score 8-10)
  ...

🔔 NOW RELEVANT (snoozed items due this week)
  ...
Plain text. No HTML.

What Claude Code needs to do

Scaffold the repo with the 4 source files + workflow YAML
fetch.py — hit both APIs, return merged deduped list of {name, url, description, stars, hn_points, age_days}
score.py — send list to Claude with rubric + your profile, parse JSON response
snooze.py — on each run, check snooze.json for items due this week, append to digest
notify.py — format and send via smtplib
weekly.yml — cron schedule, secrets wiring, auto-commit snooze.json if changed
A separate snooze_tool.yml — workflow_dispatch with tool, url, weeks inputs, runs snooze.py --add

That's the whole project. ~300 lines total across all files. Tell Claude Code to keep each file under 80 lines and add no dependencies beyond requests and anthropic.
