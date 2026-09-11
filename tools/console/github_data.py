"""Fetch GitHub telemetry for the console cards.

With a token (env PROFILE_TOKEN or GITHUB_TOKEN) the GraphQL API supplies the
contribution calendar, including private contribution counts when the token
belongs to the profile owner. Without a token, only public REST fields are
available and the activity strip stays pending.

Writes tools/console/data/telemetry.json. Standard library only.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGIN = json.loads((HERE / "data" / "profile.json").read_text(encoding="utf-8"))["handle"]
OUT = HERE / "data" / "telemetry.json"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
  }
}
"""


def _http(url: str, data: bytes | None = None, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "absaar-404-console", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _age(created: str, now: dt.datetime) -> str:
    c = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
    months = (now.year - c.year) * 12 + now.month - c.month
    y, m = divmod(max(months, 0), 12)
    if y and m:
        return f"{y}Y {m}M"
    if y:
        return f"{y}Y"
    return f"{m}M" if m else "NEW"


def _streaks(days: list[dict]) -> tuple[int, int]:
    """(current, longest) streak in days; current counts back from today or yesterday."""
    counts = [d["contributionCount"] for d in days]
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    current = 0
    idx = len(counts) - 1
    if idx >= 0 and counts[idx] == 0:
        idx -= 1  # today may not have activity yet
    while idx >= 0 and counts[idx] > 0:
        current += 1
        idx -= 1
    return current, longest


def sync() -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
    out: dict = {"login": LOGIN, "synced_at": now.strftime("%Y-%m-%d %H:%M UTC")}
    try:
        if token:
            frm = (now - dt.timedelta(days=364)).replace(hour=0, minute=0, second=0, microsecond=0)
            body = json.dumps({"query": QUERY, "variables": {"login": LOGIN, "from": frm.isoformat(), "to": now.isoformat()}}).encode()
            res = _http("https://api.github.com/graphql", body, {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
            u = res["data"]["user"]
            cal = u["contributionsCollection"]["contributionCalendar"]
            days = [d for w in cal["weeks"] for d in w["contributionDays"]]
            weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]][-52:]
            weekday = [0] * 7
            for d in days:
                weekday[(d["weekday"] - 1) % 7] += d["contributionCount"]   # GitHub: 0 = Sunday -> index 6
            cur, longest = _streaks(days)
            names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            out.update({
                "contributions_year": cal["totalContributions"],
                "restricted_contributions": u["contributionsCollection"]["restrictedContributionsCount"],
                "commits_year": u["contributionsCollection"]["totalCommitContributions"],
                "weeks": weeks, "weekday": weekday,
                "busiest_day": names[max(range(7), key=lambda i: weekday[i])] if any(weekday) else None,
                "current_streak": cur, "longest_streak": longest,
                "public_repos": u["repositories"]["totalCount"],
                "followers": u["followers"]["totalCount"],
                "account_age": _age(u["createdAt"], now),
            })
        else:
            u = _http(f"https://api.github.com/users/{LOGIN}")
            out.update({
                "public_repos": u.get("public_repos"), "followers": u.get("followers"),
                "account_age": _age(u["created_at"], now) if u.get("created_at") else None,
            })
    except (urllib.error.URLError, KeyError, TypeError, ValueError) as e:
        print(f"telemetry: fetch failed ({e}); keeping previous data", file=sys.stderr)
        if OUT.exists():
            return json.loads(OUT.read_text(encoding="utf-8"))
        return {}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"telemetry: synced {out['synced_at']} ({'graphql' if token else 'public rest'})")
    return out


if __name__ == "__main__":
    sync()
