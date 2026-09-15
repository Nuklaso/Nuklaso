"""Render the profile telemetry SVGs from live GitHub data.

Everything is drawn here instead of pulled from a third-party card service,
so the README never shows a broken image when someone else's Vercel app is
rate limited. Stdlib only - no dependencies to install in CI.

Outputs: assets/telemetry.svg, assets/repos.svg
"""

from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "Nuklaso")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets"

BG = "#07060b"
PANEL = "#0d0a17"
TRACK = "#1d1630"
LINE = "#a855f7"
DIM = "#6d5a8f"
TEXT = "#cbb6e8"
BRIGHT = "#f2e8ff"
CYAN = "#22d3ee"
PINK = "#e879f9"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

HEAT = ["#171226", "#3b1f66", "#6d28d9", "#a855f7", "#e879f9"]
WHEEL = ["#a855f7", "#22d3ee", "#e879f9", "#818cf8", "#f0abfc", "#67e8f9", "#c084fc"]


# --------------------------------------------------------------------------- io

def get(url: str, raw: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": "nuklaso-profile-generator"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    return body if raw else json.loads(body)


def fetch_profile():
    user = get(f"https://api.github.com/users/{USER}")
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
    return user, [r for r in repos if not r.get("fork")]


def fetch_languages(repos):
    totals: dict[str, int] = defaultdict(int)
    for repo in repos:
        try:
            for lang, size in get(f"https://api.github.com/repos/{repo['full_name']}/languages").items():
                totals[lang] += size
        except urllib.error.HTTPError:
            continue
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


def fetch_contributions():
    """Parse the public contribution calendar (no auth required)."""
    html = get(f"https://github.com/users/{USER}/contributions", raw=True)

    counts: dict[str, int] = {}
    for cell_id, text in re.findall(r'for="(contribution-day-component-[^"]+)"[^>]*>([^<]*)<', html):
        match = re.match(r"([\d,]+) contribution", text)
        counts[cell_id] = int(match.group(1).replace(",", "")) if match else 0

    days = []
    for tag in re.findall(r"<td[^>]*class=\"ContributionCalendar-day\"[^>]*>", html):
        day = dict(re.findall(r'([a-z-]+)="([^"]*)"', tag))
        if not day.get("data-date"):
            continue
        days.append({
            "date": day["data-date"],
            "level": int(day.get("data-level", 0)),
            "week": int(day.get("data-ix", 0)),
            "row": int(day["id"].rsplit("-", 2)[1]),
            "count": counts.get(day.get("id", ""), 0),
        })
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    """Current and longest run of consecutive days with at least one contribution."""
    today = date.today().isoformat()

    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)

    current = 0
    for day in reversed(days):
        if day["date"] > today:
            continue
        if day["count"] > 0:
            current += 1
        elif day["date"] != today:
            break
    return current, longest


# ----------------------------------------------------------------------- pieces

def shell(width: int, height: int, title: str, right: str, body: str, label: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<defs>
  <linearGradient id="num" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#c084fc"/><stop offset="100%" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{LINE}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{CYAN}" stop-opacity=".9"/>
    <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="mesh" width="26" height="26" patternUnits="userSpaceOnUse">
    <circle cx="1.5" cy="1.5" r="1" fill="{LINE}" opacity=".12"/>
  </pattern>
</defs>
<rect width="{width}" height="{height}" fill="{BG}"/>
<rect width="{width}" height="{height}" fill="url(#mesh)"/>
<g font-family="{MONO}">
  <text x="64" y="52" fill="{CYAN}" font-size="13" letter-spacing="4">{escape(title)}</text>
  <text x="{width - 64}" y="52" fill="{DIM}" font-size="12" letter-spacing="2" text-anchor="end">{escape(right)}</text>
  <line x1="64" y1="66" x2="{width - 64}" y2="66" stroke="{LINE}" stroke-opacity=".22"/>
{body}
</g>
</svg>
"""


def sublabel(x: float, y: float, text: str) -> str:
    return f'  <text x="{x}" y="{y}" fill="{DIM}" font-size="11" letter-spacing="2.6">{escape(text)}</text>'


def wrap(text: str, width: int, lines: int) -> list[str]:
    words, out, cur = (text or "").split(), [], ""
    for word in words:
        candidate = f"{cur} {word}".strip()
        if len(candidate) > width and cur:
            out.append(cur)
            cur = word
            if len(out) == lines:
                break
        else:
            cur = candidate
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and " ".join(out) != " ".join(words):
        out[-1] = out[-1][: width - 1].rstrip() + "…"
    return out


def human(n: int) -> str:
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


# --------------------------------------------------------------------- telemetry

def tiles_block(user, repos, days, languages, longest) -> str:
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    stars = sum(r.get("stargazers_count", 0) for r in repos)

    tiles = [
        (human(total), "CONTRIBUTIONS"),
        (str(active), "ACTIVE DAYS"),
        (str(longest), "LONGEST STREAK"),
        (str(len(repos)), "REPOSITORIES"),
        (str(len(languages)), "LANGUAGES"),
        (human(stars + user.get("followers", 0)), "STARS + FOLLOWERS"),
    ]

    out = []
    for i, (value, label) in enumerate(tiles):
        x = 64 + i * 179
        out.append(f"""  <g transform="translate({x},92)">
    <rect width="161" height="104" rx="10" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".28"/>
    <rect x="18" y="0" width="125" height="2" fill="url(#edge)">
      <animate attributeName="opacity" values=".25;1;.25" dur="3.4s" begin="-{i * 0.45:.2f}s" repeatCount="indefinite"/>
    </rect>
    <text x="80" y="58" text-anchor="middle" fill="url(#num)" font-size="38" font-weight="bold">{value}</text>
    <text x="80" y="82" text-anchor="middle" fill="{DIM}" font-size="9.5" letter-spacing="1.6">{label}</text>
  </g>""")
    return "\n".join(out)


def languages_block(languages, top_y: float) -> str:
    top = list(languages.items())[:6]
    total = sum(v for _, v in top) or 1
    cx, cy, r, sw = 236, top_y + 90, 84, 30
    circumference = 2 * math.pi * r

    out = [sublabel(64, top_y - 8, "LANGUAGES BY BYTES SHIPPED"),
           f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" stroke-width="{sw}"/>']

    offset = 0.0
    for i, (name, size) in enumerate(top):
        dash = circumference * size / total
        colour = WHEEL[i % len(WHEEL)]
        out.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" stroke-width="{sw}" '
                   f'stroke-dasharray="0 {circumference:.1f}" stroke-dashoffset="{-offset:.1f}" '
                   f'transform="rotate(-90 {cx} {cy})">'
                   f'<animate attributeName="stroke-dasharray" from="0 {circumference:.1f}" '
                   f'to="{dash:.1f} {circumference - dash:.1f}" dur=".9s" begin="{i * 0.14:.2f}s" fill="freeze"/></circle>')
        offset += dash

    out.append(f'  <text x="{cx}" y="{cy - 2}" text-anchor="middle" fill="{BRIGHT}" font-size="26" font-weight="bold">{len(languages)}</text>')
    out.append(f'  <text x="{cx}" y="{cy + 20}" text-anchor="middle" fill="{DIM}" font-size="9.5" letter-spacing="1.8">LANGUAGES</text>')

    legend_top = cy - (len(top) * 42) / 2 + 20
    for i, (name, size) in enumerate(top):
        y = legend_top + i * 42
        pct = 100 * size / total
        colour = WHEEL[i % len(WHEEL)]
        out.append(f'  <circle cx="404" cy="{y - 5}" r="5" fill="{colour}"/>')
        out.append(f'  <text x="424" y="{y}" fill="{TEXT}" font-size="14">{escape(name.lower())}</text>')
        out.append(f'  <text x="1136" y="{y}" text-anchor="end" fill="{DIM}" font-size="13">{pct:.1f}%</text>')
        out.append(f'  <rect x="660" y="{y - 12}" width="420" height="8" rx="4" fill="{TRACK}"/>')
        out.append(f'  <rect x="660" y="{y - 12}" width="0" height="8" rx="4" fill="{colour}">'
                   f'<animate attributeName="width" from="0" to="{420 * size / total:.1f}" dur=".9s" '
                   f'begin="{i * 0.14:.2f}s" fill="freeze"/></rect>')
    return "\n".join(out)


def heatmap_block(days, top_y: float) -> str:
    cell, gap, x0 = 14, 4, 100
    y0 = top_y + 26
    out = [sublabel(64, top_y - 8, "CONTRIBUTION SIGNAL · LAST 12 MONTHS")]
    months, seen = [], set()

    for day in days:
        x = x0 + day["week"] * (cell + gap)
        y = y0 + day["row"] * (cell + gap)
        fill = HEAT[min(day["level"], 4)]
        out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}" opacity="0">'
                   f'<animate attributeName="opacity" from="0" to="1" dur=".45s" begin="{day["week"] * 0.022:.2f}s" fill="freeze"/></rect>')
        stamp = datetime.strptime(day["date"], "%Y-%m-%d")
        key = stamp.strftime("%Y-%m")
        if day["row"] == 0 and stamp.day <= 7 and key not in seen:
            seen.add(key)
            months.append((x, stamp.strftime("%b").lower()))

    for x, name in months:
        out.append(f'  <text x="{x}" y="{y0 - 10}" fill="{DIM}" font-size="10.5" letter-spacing="1.4">{name}</text>')
    for row, name in ((1, "mon"), (3, "wed"), (5, "fri")):
        out.append(f'  <text x="{x0 - 14}" y="{y0 + row * (cell + gap) + 11}" text-anchor="end" fill="{DIM}" font-size="10.5">{name}</text>')

    legend_y = y0 + 7 * (cell + gap) + 22
    legend_x = 1136 - 5 * (cell + gap) - 44
    out.append(f'  <text x="{legend_x - 10}" y="{legend_y + 12}" text-anchor="end" fill="{DIM}" font-size="10.5" letter-spacing="1.4">quiet</text>')
    for i, colour in enumerate(HEAT):
        out.append(f'  <rect x="{legend_x + i * (cell + gap)}" y="{legend_y}" width="{cell}" height="{cell}" rx="3" fill="{colour}"/>')
    out.append(f'  <text x="{legend_x + 5 * (cell + gap) + 4}" y="{legend_y + 12}" fill="{DIM}" font-size="10.5" letter-spacing="1.4">loud</text>')
    return "\n".join(out)


def render_telemetry(user, repos, days, languages, longest) -> str:
    body = [
        tiles_block(user, repos, days, languages, longest),
        f'  <line x1="64" y1="240" x2="1136" y2="240" stroke="{LINE}" stroke-opacity=".14"/>',
        languages_block(languages, 274),
        f'  <line x1="64" y1="486" x2="1136" y2="486" stroke="{LINE}" stroke-opacity=".14"/>',
        heatmap_block(days, 520),
        f'  <text x="64" y="712" fill="{DIM}" font-size="11" letter-spacing="1.6">'
        f'rendered from the github api by .github/scripts/gen_profile_svgs.py &#183; '
        f'last sync {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</text>',
        f'  <circle cx="1136" cy="708" r="4" fill="{CYAN}">'
        f'<animate attributeName="opacity" values="1;.15;1" dur="1.8s" repeatCount="indefinite"/></circle>',
    ]
    return shell(1200, 742, "05 · TELEMETRY", "SELF-RENDERED · NO THIRD PARTY CARDS",
                 "\n".join(body), "telemetry")


# ------------------------------------------------------------------------ repos

def render_repos(repos) -> str:
    picks = [r for r in repos if r["name"].lower() != USER.lower()][:3]
    out = []
    for i, repo in enumerate(picks):
        x = 64 + i * 364
        lines = wrap(repo.get("description") or "No description yet.", 38, 3)
        desc = "".join(f'<tspan x="{x + 26}" dy="{0 if j == 0 else 21}">{escape(line)}</tspan>'
                       for j, line in enumerate(lines))
        colour = WHEEL[i % len(WHEEL)]
        pushed = (repo.get("pushed_at") or "")[:10]
        out.append(f"""  <g>
    <rect x="{x}" y="96" width="336" height="200" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".28"/>
    <rect x="{x + 22}" y="96" width="292" height="2" fill="url(#edge)">
      <animate attributeName="opacity" values=".25;1;.25" dur="3.6s" begin="-{i * 0.6:.2f}s" repeatCount="indefinite"/>
    </rect>
    <text x="{x + 26}" y="130" fill="{DIM}" font-size="11" letter-spacing="2">0{i + 1}</text>
    <text x="{x + 26}" y="160" fill="{CYAN}" font-size="16" font-weight="bold">{escape(repo['name'])}</text>
    <text x="{x + 26}" y="192" fill="{TEXT}" font-size="12.5">{desc}</text>
    <line x1="{x + 26}" y1="248" x2="{x + 310}" y2="248" stroke="{LINE}" stroke-opacity=".16"/>
    <circle cx="{x + 31}" cy="271" r="5" fill="{colour}"/>
    <text x="{x + 44}" y="276" fill="{DIM}" font-size="12">{escape(repo.get('language') or 'text')}</text>
    <text x="{x + 186}" y="276" fill="{DIM}" font-size="12">&#9733; {repo.get('stargazers_count', 0)}</text>
    <text x="{x + 310}" y="276" text-anchor="end" fill="{DIM}" font-size="11">{pushed}</text>
  </g>""")
    return shell(1200, 340, "04 · LATEST SIGNALS", "PUSHED MOST RECENTLY",
                 "\n".join(out), "repositories")


# ------------------------------------------------------------------------- main

def main() -> None:
    user, repos = fetch_profile()
    days = fetch_contributions()
    _, longest = streaks(days)
    languages = fetch_languages(repos)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, markup in {
        "telemetry.svg": render_telemetry(user, repos, days, languages, longest),
        "repos.svg": render_repos(repos),
    }.items():
        (OUT / name).write_text(markup, encoding="utf-8", newline="\n")
        print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
