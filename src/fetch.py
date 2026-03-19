"""Fetch emerging dev tools from Hacker News and GitHub."""

import requests
from datetime import datetime, timedelta, timezone


KEYWORDS = ["AI", "LLM", "agent", "MCP", "Claude", "GPT", "coding assistant",
            "dev tool", "developer tool", "CLI", "SDK"]

GITHUB_TOPICS = ["llm", "agent", "mcp", "claude", "ai-agent", "developer-tools"]


def fetch_hn() -> list[dict]:
    """Fetch recent Show HN posts matching dev-tool keywords."""
    week_ago = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
    query = " ".join(KEYWORDS[:5])  # Algolia does implicit OR on terms
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "query": query,
        "tags": "show_hn",
        "numericFilters": f"created_at_i>{week_ago}",
        "hitsPerPage": 30,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[fetch] HN fetch failed: {e}")
        return []

    now = datetime.now(timezone.utc)
    tools = []
    for hit in resp.json().get("hits", []):
        created = datetime.fromtimestamp(hit["created_at_i"], tz=timezone.utc)
        tools.append({
            "name": hit.get("title", "").replace("Show HN: ", ""),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
            "description": hit.get("title", ""),
            "stars": 0,
            "hn_points": hit.get("points", 0),
            "age_days": (now - created).days,
        })
    return tools


def fetch_github() -> list[dict]:
    """Fetch trending new repos from GitHub matching dev-tool topics."""
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    url = "https://api.github.com/search/repositories"
    now = datetime.now(timezone.utc)
    seen_urls: set[str] = set()
    tools: list[dict] = []

    for topic in GITHUB_TOPICS:
        q = f"created:>{week_ago} topic:{topic}"
        params = {"q": q, "sort": "stars", "order": "desc", "per_page": 10}
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[fetch] GitHub fetch failed for topic:{topic}: {e}")
            continue

        for repo in resp.json().get("items", []):
            if repo["html_url"] in seen_urls:
                continue
            seen_urls.add(repo["html_url"])
            created = datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
            tools.append({
                "name": repo["full_name"].split("/")[-1],
                "url": repo["html_url"],
                "description": repo.get("description") or "",
                "stars": repo.get("stargazers_count", 0),
                "hn_points": 0,
                "age_days": (now - created).days,
            })

    tools.sort(key=lambda t: t["stars"], reverse=True)
    return tools[:30]


def fetch_all() -> list[dict]:
    """Fetch from all sources, dedupe by URL, cap at 25."""
    hn = fetch_hn()
    gh = fetch_github()
    seen: set[str] = set()
    merged: list[dict] = []
    for tool in hn + gh:
        if tool["url"] not in seen:
            seen.add(tool["url"])
            merged.append(tool)
    return merged[:25]
