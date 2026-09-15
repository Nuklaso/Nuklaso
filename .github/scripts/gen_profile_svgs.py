"""Render the profile telemetry SVGs from live GitHub data.

Everything is drawn here instead of pulled from a third-party card service,
so the README never shows a broken image when someone else's Vercel app is
rate limited. Stdlib only - no dependencies to install in CI.

Outputs: assets/stats.svg, assets/heatmap.svg, assets/langs.svg, assets/repos.svg
"""

from __future__ import annotations

import json
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

BG = "#08070c"
PANEL = "#0c0a12"
LINE = "#a855f7"
DIM = "#6d5a8f"
TEXT = "#cbb6e8"
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

def shell(width: int, height: int, title: str, body: str, label: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<defs>
  <linearGradient id="num" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{LINE}"/><stop offset="100%" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{LINE}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{CYAN}" stop-opacity=".9"/>
    <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="1.5" cy="1.5" r="1.1" fill="{LINE}" opacity=".14"/>
  </pattern>
</defs>
<rect width="{width}" height="{height}" fill="{BG}"/>
<rect width="{width}" height="{height}" fill="url(#dots)"/>
<g font-family="{MONO}">
  <text x="60" y="52" fill="{CYAN}" font-size="13" letter-spacing="4">{escape(title)}</text>
  <line x1="60" y1="66" x2="{width - 60}" y2="66" stroke="{LINE}" stroke-opacity=".22"/>
{body}
</g>
</svg>
"""


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


# ------------------------------------------------------------------------ cards

def render_stats(user, repos, days, languages, longest) -> str:
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

    body = []
    for i, (value, label) in enumerate(tiles):
        x = 60 + i * 183
        body.append(f"""  <g transform="translate({x},96)">
    <rect width="165" height="104" rx="10" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".30"/>
    <rect x="18" y="0" width="129" height="2" fill="url(#edge)">
      <animate attributeName="opacity" values=".25;1;.25" dur="3.4s" begin="-{i * 0.45:.2f}s" repeatCount="indefinite"/>
    </rect>
    <text x="82" y="58" text-anchor="middle" fill="url(#num)" font-size="38" font-weight="bold">{value}</text>
    <text x="82" y="82" text-anchor="middle" fill="{DIM}" font-size="9.5" letter-spacing="1.6">{label}</text>
  </g>""")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body.append(f'  <text x="60" y="234" fill="{DIM}" font-size="11" letter-spacing="1.6">'
                f'last sync {stamp} &#183; rendered from the github api, not a third party card</text>')
    body.append(f'  <circle cx="1134" cy="230" r="4" fill="{CYAN}">'
                f'<animate attributeName="opacity" values="1;.15;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    return shell(1200, 250, "05 · TELEMETRY", "\n".join(body), "telemetry")


def render_heatmap(days) -> str:
    cell, gap, x0, y0 = 14, 4, 96, 96
    weeks = max((d["week"] for d in days), default=52)
    body, months, seen = [], [], set()

    for day in days:
        x = x0 + day["week"] * (cell + gap)
        y = y0 + day["row"] * (cell + gap)
        fill = HEAT[min(day["level"], 4)]
        delay = day["week"] * 0.022
        body.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}" opacity="0">'
                    f'<animate attributeName="opacity" from="0" to="1" dur=".45s" begin="{delay:.2f}s" fill="freeze"/></rect>')
        stamp = datetime.strptime(day["date"], "%Y-%m-%d")
        key = stamp.strftime("%Y-%m")
        if day["row"] == 0 and stamp.day <= 7 and key not in seen:
            seen.add(key)
            months.append((x, stamp.strftime("%b").lower()))

    for x, name in months:
        body.append(f'  <text x="{x}" y="{y0 - 14}" fill="{DIM}" font-size="10.5" letter-spacing="1.4">{name}</text>')
    for row, name in ((1, "mon"), (3, "wed"), (5, "fri")):
        body.append(f'  <text x="{x0 - 14}" y="{y0 + row * (cell + gap) + 11}" text-anchor="end" '
                    f'fill="{DIM}" font-size="10.5">{name}</text>')

    legend_x = 1140 - 5 * (cell + gap) - 40
    body.append(f'  <text x="{legend_x - 10}" y="{y0 + 7 * (cell + gap) + 30}" text-anchor="end" fill="{DIM}" font-size="10.5" letter-spacing="1.4">quiet</text>')
    for i, colour in enumerate(HEAT):
        body.append(f'  <rect x="{legend_x + i * (cell + gap)}" y="{y0 + 7 * (cell + gap) + 18}" '
                    f'width="{cell}" height="{cell}" rx="3" fill="{colour}"/>')
    body.append(f'  <text x="{legend_x + 5 * (cell + gap) + 4}" y="{y0 + 7 * (cell + gap) + 30}" fill="{DIM}" font-size="10.5" letter-spacing="1.4">loud</text>')

    height = y0 + 7 * (cell + gap) + 56
    return shell(1200, height, "06 · SIGNAL TRACE · LAST 12 MONTHS", "\n".join(body), "contribution heatmap")


def render_langs(languages) -> str:
    top = list(languages.items())[:6]
    total = sum(v for _, v in top) or 1
    cx, cy, r, sw = 250, 190, 92, 34
    circumference = 2 * 3.14159265 * r

    body, offset = [], 0.0
    body.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1d1630" stroke-width="{sw}"/>')
    for i, (name, size) in enumerate(top):
        frac = size / total
        dash = circumference * frac
        colour = WHEEL[i % len(WHEEL)]
        body.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" stroke-width="{sw}" '
                    f'stroke-dasharray="0 {circumference:.1f}" stroke-dashoffset="{-offset:.1f}" '
                    f'transform="rotate(-90 {cx} {cy})" stroke-linecap="butt">'
                    f'<animate attributeName="stroke-dasharray" from="0 {circumference:.1f}" '
                    f'to="{dash:.1f} {circumference - dash:.1f}" dur=".9s" begin="{i * 0.14:.2f}s" fill="freeze"/></circle>')
        offset += dash

    body.append(f'  <text x="{cx}" y="{cy - 4}" text-anchor="middle" fill="#f2e8ff" font-size="26" font-weight="bold">{len(languages)}</text>')
    body.append(f'  <text x="{cx}" y="{cy + 18}" text-anchor="middle" fill="{DIM}" font-size="10" letter-spacing="1.8">LANGUAGES</text>')

    legend_top = cy - (len(top) * 44) / 2 + 22
    for i, (name, size) in enumerate(top):
        y = legend_top + i * 44
        pct = 100 * size / total
        colour = WHEEL[i % len(WHEEL)]
        body.append(f'  <circle cx="470" cy="{y - 5}" r="5" fill="{colour}"/>')
        body.append(f'  <text x="490" y="{y}" fill="{TEXT}" font-size="14">{escape(name.lower())}</text>')
        body.append(f'  <text x="1140" y="{y}" text-anchor="end" fill="{DIM}" font-size="13">{pct:.1f}%</text>')
        body.append(f'  <rect x="700" y="{y - 12}" width="380" height="8" rx="4" fill="#2a2040"/>')
        body.append(f'  <rect x="700" y="{y - 12}" width="0" height="8" rx="4" fill="{colour}">'
                    f'<animate attributeName="width" from="0" to="{380 * size / total:.1f}" dur=".9s" '
                    f'begin="{i * 0.14:.2f}s" fill="freeze"/></rect>')

    return shell(1200, 330, "04 · LANGUAGES BY BYTES SHIPPED", "\n".join(body), "languages")


def render_repos(repos) -> str:
    picks = [r for r in repos if r["name"].lower() != USER.lower()][:3]
    body = []
    for i, repo in enumerate(picks):
        x = 60 + i * 370
        lines = wrap(repo.get("description") or "No description yet.", 40, 3)
        desc = "".join(
            f'<tspan x="{x + 24}" dy="{0 if j == 0 else 20}">{escape(line)}</tspan>'
            for j, line in enumerate(lines)
        )
        colour = WHEEL[i % len(WHEEL)]
        pushed = (repo.get("pushed_at") or "")[:10]
        body.append(f"""  <g>
    <rect x="{x}" y="96" width="340" height="186" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".30"/>
    <rect x="{x + 20}" y="96" width="300" height="2" fill="url(#edge)">
      <animate attributeName="opacity" values=".25;1;.25" dur="3.6s" begin="-{i * 0.6:.2f}s" repeatCount="indefinite"/>
    </rect>
    <text x="{x + 24}" y="136" fill="{CYAN}" font-size="16" font-weight="bold">{escape(repo['name'])}</text>
    <text x="{x + 24}" y="166" fill="{TEXT}" font-size="12.5">{desc}</text>
    <circle cx="{x + 29}" cy="{252}" r="5" fill="{colour}"/>
    <text x="{x + 42}" y="257" fill="{DIM}" font-size="12">{escape(repo.get('language') or 'text')}</text>
    <text x="{x + 200}" y="257" fill="{DIM}" font-size="12">&#9733; {repo.get('stargazers_count', 0)}</text>
    <text x="{x + 316}" y="257" text-anchor="end" fill="{DIM}" font-size="11">{pushed}</text>
  </g>""")
    return shell(1200, 320, "03 · LATEST SIGNALS", "\n".join(body), "repositories")


# ------------------------------------------------------------------------- main

def main() -> None:
    user, repos = fetch_profile()
    days = fetch_contributions()
    _, longest = streaks(days)
    languages = fetch_languages(repos)

    OUT.mkdir(parents=True, exist_ok=True)
    written = {
        "stats.svg": render_stats(user, repos, days, languages, longest),
        "heatmap.svg": render_heatmap(days),
        "langs.svg": render_langs(languages),
        "repos.svg": render_repos(repos),
    }
    for name, markup in written.items():
        (OUT / name).write_text(markup, encoding="utf-8", newline="\n")
        print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
