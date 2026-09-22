#!/usr/bin/env python3
"""Fetch a GitHub user's public contribution calendar -- no token, no
GraphQL API. GitHub serves it as an HTML fragment at
https://github.com/users/<username>/contributions, the same partial the
profile page itself uses. Parse it with BeautifulSoup and write
data/contributions.json with the raw days plus a few derived stats.
"""
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Morioh06"
URL = "https://github.com/users/{username}/contributions"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days(username: str) -> list[dict]:
    resp = requests.get(
        URL.format(username=username),
        headers={"User-Agent": "profile-readme-bot (+https://github.com)"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        day = td.get("data-date")
        if not day:
            continue
        level_raw = td.get("data-level")
        count = 0
        tip_id = td.get("id")
        if tip_id:
            tip = soup.select_one(f'tool-tip[for="{tip_id}"]')
            if tip:
                m = re.match(r"([\d,]+)\s+contribution", tip.get_text(strip=True))
                if m:
                    count = int(m.group(1).replace(",", ""))
        days.append(
            {
                "date": day,
                "count": count,
                "level": int(level_raw) if level_raw is not None else None,
            }
        )

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    today = date.today()
    by_date = {datetime.strptime(d["date"], "%Y-%m-%d").date(): d["count"] for d in days}

    current_streak = 0
    cursor = today
    if by_date.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    while by_date.get(cursor, 0) > 0:
        current_streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    monthly: dict[str, int] = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly": monthly,
    }


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    days = fetch_days(username)
    stats = compute_stats(days)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "username": username,
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "days": days,
                "stats": stats,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH} ({len(days)} days, {stats.get('total', 0)} contributions)")


if __name__ == "__main__":
    main()
