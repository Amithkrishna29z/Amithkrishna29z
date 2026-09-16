#!/usr/bin/env python3
"""Renders assets/achievements.svg from the GitHub API.

Replaces github-profile-trophy.vercel.app, which started returning HTTP 402
DEPLOYMENT_DISABLED and left a broken image on the profile. Self-hosted, so the
worst failure mode is now stale numbers rather than a broken image.

Cards are chosen from a candidate list at render time: anything that errors or
comes back zero is skipped, and the first six survivors are drawn. Stdlib only.
"""
import datetime
import json
import os
import pathlib
import urllib.request

USER = "Amithkrishna29z"
API = "https://api.github.com"
OUT = pathlib.Path(__file__).resolve().parent / "achievements.svg"

W, H = 900, 124
GAP, MAX_CARDS = 12, 6

BG, EDGE, LABEL, VALUE = "#0d1117", "#30363d", "#8b949e", "#e6edf3"
PINK, YELLOW, CYAN, PURPLE, GREEN, ORANGE = (
    "#f75c7e", "#fbbf24", "#22d3ee", "#8a2be2", "#3fb950", "#ff8c42")

# 24x24 octicon-ish glyphs, stroked so one colour drives the whole card
ICONS = {
    "repo":   "M3 2.5h13a1.5 1.5 0 0 1 1.5 1.5v16a1.5 1.5 0 0 0-1.5-1.5H3z M3 2.5v18",
    "commit": "M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z M12 2.5v6 M12 15.5v6",
    "code":   "M8.5 6.5L3 12l5.5 5.5 M15.5 6.5L21 12l-5.5 5.5",
    "pulse":  "M2.5 12h4l2.5-7 4 14 2.5-7h6",
    "pr":     "M6 7.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z M6 21.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z M6 7.5v9 M18 21.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z M18 16.5V9a3 3 0 0 0-3-3h-4",
    "clock":  "M12 21.5a9.5 9.5 0 1 0 0-19 9.5 9.5 0 0 0 0 19z M12 6.5V12l3.5 2.5",
    "star":   "M12 2.5l2.9 5.9 6.6.9-4.8 4.6 1.2 6.5-5.9-3.1-5.9 3.1 1.2-6.5L2.5 9.3l6.6-.9z",
    "users":  "M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z M2.5 20a6.5 6.5 0 0 1 13 0 M16.5 5.2a3.5 3.5 0 0 1 0 6.6 M18 14.2a6.5 6.5 0 0 1 3.5 5.8",
}


def get(path):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": USER + "-profile-readme",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search_count(query):
    """Search API needs a token. Returns None rather than failing the render."""
    try:
        return get("/search/%s&per_page=1" % query)["total_count"]
    except Exception as e:
        print("  ! skipped %s (%s)" % (query, e))
        return None


def collect():
    user = get("/users/%s" % USER)
    repos, page = [], 1
    while True:
        batch = get("/users/%s/repos?per_page=100&page=%d" % (USER, page))
        repos += batch
        if len(batch) < 100:
            break
        page += 1

    owned = [r for r in repos if not r["fork"]]
    now = datetime.datetime.now(datetime.timezone.utc)

    def age_days(ts):
        return (now - datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                .replace(tzinfo=datetime.timezone.utc)).days

    active = sum(1 for r in owned if age_days(r["pushed_at"]) <= 365)
    years = age_days(user["created_at"]) / 365.25

    # ordered by preference; zeros and failures drop out
    candidates = [
        ("repo",   user["public_repos"],                                  "Repositories",    PINK),
        ("commit", search_count("commits?q=author:%s" % USER),            "Commits",         YELLOW),
        ("code",   len({r["language"] for r in owned if r["language"]}),  "Languages",       CYAN),
        ("pulse",  active,                                                "Active this year", PURPLE),
        ("pr",     search_count("issues?q=author:%s+type:pr" % USER),     "Pull requests",   GREEN),
        ("clock",  round(years, 1),                                       "Years on GitHub", ORANGE),
        ("star",   sum(r["stargazers_count"] for r in owned),             "Stars earned",    YELLOW),
        ("users",  user["followers"],                                     "Followers",       PURPLE),
    ]
    return [c for c in candidates if c[1]][:MAX_CARDS]


def render(stats):
    n = len(stats)
    cw = (W - GAP * (n - 1)) / n
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'font-family="ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace" '
         'role="img" aria-label="%s">'
         % (W, H, W, H, ", ".join("%s %s" % (s[1], s[2].lower()) for s in stats))]

    for i, (icon, value, label, colour) in enumerate(stats):
        o.append('<g transform="translate(%.2f,0)">' % (i * (cw + GAP)))
        o.append('<rect x="0.75" y="0.75" width="%.2f" height="%.2f" rx="10" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (cw - 1.5, H - 1.5, BG, EDGE))
        o.append('<path d="M11 1.5h%.2f" stroke="%s" stroke-width="3" stroke-linecap="round"/>'
                 % (cw - 22, colour))
        o.append('<g transform="translate(%.2f,24) scale(0.9)" fill="none" stroke="%s" '
                 'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">'
                 % (cw / 2 - 10.8, colour))
        o.append('<path d="%s"/>' % ICONS[icon])
        o.append('</g>')
        o.append('<text x="%.2f" y="79" text-anchor="middle" font-size="27" font-weight="700" fill="%s">%s</text>'
                 % (cw / 2, VALUE, value))
        o.append('<text x="%.2f" y="100" text-anchor="middle" font-size="10" letter-spacing="0.6" fill="%s">%s</text>'
                 % (cw / 2, LABEL, label.upper()))
        o.append('</g>')

    o.append('</svg>')
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    stats = collect()
    OUT.write_text(render(stats), encoding="utf-8")
    print("wrote %s (%d bytes, %d cards)" % (OUT, OUT.stat().st_size, len(stats)))
    for _, v, label, _c in stats:
        print("  %-18s %s" % (label, v))
