"""Replay a real game of 2048byNiklas and freeze it into an animated SVG.

The engine is not vendored here - it is downloaded straight from the project
repository, played headless, and every board state is recorded. The resulting
assets/game.svg is therefore an actual game the expectimax AI played, not an
illustration of one.

    python .github/scripts/render_game.py --seed 11 --budget 300
    python .github/scripts/render_game.py --json game.json   # reuse a recording

Pure standard library, same as the engine it drives.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ENGINE_URL = "https://raw.githubusercontent.com/Nuklaso/2048byNiklas/main/engine.py"
OUT = Path(__file__).resolve().parents[2] / "assets" / "game.svg"

BG = "#07060b"
PANEL = "#0d0a17"
GRID = "#171029"
LINE = "#a855f7"
DIM = "#6d5a8f"
TEXT = "#cbb6e8"
BRIGHT = "#f2e8ff"
CYAN = "#22d3ee"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# tile value -> (fill, text colour, glow?)
TILES = {
    2: ("#221a30", "#8b7aa8", False),
    4: ("#2d2142", "#a48fc4", False),
    8: ("#43276e", "#d9c8f0", False),
    16: ("#5b21b6", "#ede9fe", False),
    32: ("#7c3aed", "#f5f3ff", False),
    64: ("#a855f7", "#faf5ff", False),
    128: ("#c026d3", "#fdf4ff", True),
    256: ("#e879f9", "#2a0640", True),
    512: ("#f0abfc", "#2a0640", True),
    1024: ("#22d3ee", "#062a33", True),
    2048: ("#67e8f9", "#062a33", True),
    4096: ("#ecfeff", "#0b3b44", True),
    8192: ("#ffffff", "#0b3b44", True),
}

ARROWS = {"up": "↑", "down": "↓", "left": "←", "right": "→"}


# ------------------------------------------------------------------ recording

def load_engine():
    src = urllib.request.urlopen(ENGINE_URL, timeout=30).read().decode("utf-8")
    path = Path(tempfile.mkdtemp()) / "engine.py"
    path.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("nuklaso_engine", path)
    engine = importlib.util.module_from_spec(spec)
    sys.modules["nuklaso_engine"] = engine
    spec.loader.exec_module(engine)
    engine.build_tables()
    return engine


def record(seed: int, budget: float) -> dict:
    engine = load_engine()
    dirs = ["up", "down", "left", "right"]
    ai = engine.AI2048()
    rng = random.Random(seed)
    board = engine.new_board(rng)
    score = 0
    frames = [{"grid": engine.board_to_grid(board), "score": 0, "move": None}]
    start = time.time()
    while time.time() - start < budget:
        mv = ai.best_move(board)
        if mv == -1:
            break
        score += engine.move_score(board, mv)
        board = engine.spawn_tile(engine.MOVES[mv](board), rng)
        frames.append({"grid": engine.board_to_grid(board), "score": score, "move": dirs[mv]})
    return {"seed": seed, "frames": frames, "moves": len(frames) - 1,
            "score": score, "max_tile": engine.max_tile(board)}


# ------------------------------------------------------------------- sampling

def sample(frames: list, target: int) -> list[int]:
    """Evenly spaced frames, plus the frame where each new best tile appears."""
    keep = {0, len(frames) - 1}
    keep.update(round(i * (len(frames) - 1) / (target - 1)) for i in range(target))

    best = 0
    for i, frame in enumerate(frames):
        top = max(max(row) for row in frame["grid"])
        if top > best:
            best = top
            if top >= 128:
                keep.add(i)
    return sorted(keep)


# -------------------------------------------------------------------- drawing

def tile(x: int, y: int, size: int, value: int) -> str:
    fill, ink, glow = TILES.get(value, ("#ffffff", "#0b3b44", True))
    digits = len(str(value))
    font = 36 if digits <= 2 else (31 if digits == 3 else 25)
    halo = (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="9" fill="{fill}" '
            f'opacity=".45" filter="url(#tileGlow)"/>') if glow else ""
    return (f'{halo}<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="9" fill="{fill}"/>'
            f'<text x="{x + size / 2}" y="{y + size / 2 + font * 0.35:.0f}" text-anchor="middle" '
            f'fill="{ink}" font-size="{font}" font-weight="bold">{value}</text>')


def render(game: dict, frame_count: int, frame_seconds: float, hold_seconds: float) -> str:
    frames = game["frames"]
    picks = sample(frames, frame_count)
    total = len(picks) * frame_seconds + hold_seconds
    board_x, board_y, size, gap = 76, 132, 100, 12

    groups = []
    for slot, index in enumerate(picks):
        frame = frames[index]
        start = slot * frame_seconds
        end = start + frame_seconds + (hold_seconds if slot == len(picks) - 1 else 0)
        k1, k2 = start / total, (start + 0.001) / total
        k3, k4 = end / total, min((end + 0.001) / total, 1)

        parts = []
        for r, row in enumerate(frame["grid"]):
            for c, value in enumerate(row):
                if value:
                    parts.append(tile(board_x + c * (size + gap), board_y + r * (size + gap), size, value))

        top = max(max(row) for row in frame["grid"])
        arrow = ARROWS.get(frame["move"] or "", "·")
        parts.append(f'<text x="640" y="236" fill="{BRIGHT}" font-size="46" font-weight="bold">{frame["score"]:,}</text>')
        parts.append(f'<text x="640" y="352" fill="{CYAN}" font-size="30" font-weight="bold">{index:,}</text>')
        parts.append(f'<text x="860" y="352" fill="{CYAN}" font-size="30" font-weight="bold">{top:,}</text>')
        parts.append(f'<text x="1080" y="352" fill="{BRIGHT}" font-size="30" font-weight="bold" text-anchor="middle">{arrow}</text>')

        groups.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" '
            f'keyTimes="0;{k1:.5f};{k2:.5f};{k3:.5f};{k4:.5f}" dur="{total:.2f}s" '
            f'calcMode="discrete" repeatCount="indefinite"/>{"".join(parts)}</g>')

    cells = "".join(
        f'<rect x="{board_x + c * (size + gap)}" y="{board_y + r * (size + gap)}" '
        f'width="{size}" height="{size}" rx="9" fill="{GRID}"/>'
        for r in range(4) for c in range(4))

    facts = [
        "64-bit bitboard, 16 tiles in 16 nibbles",
        "expectimax with real chance nodes (90/10)",
        "65,536 precomputed row tables, up/down via transpose",
        "transposition table + probability cutoff pruning",
        "adaptive depth 3-6, deeper as the board fills",
    ]
    fact_rows = "".join(
        f'<circle cx="646" cy="{418 + i * 30}" r="3" fill="{LINE}" opacity=".8"/>'
        f'<text x="662" y="{423 + i * 30}" fill="{TEXT}" font-size="13.5">{f}</text>'
        for i, f in enumerate(facts))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 640" width="1200" height="640" role="img" aria-label="the 2048 AI playing a real game">
<title>2048byNiklas - expectimax replay</title>
<defs>
  <radialGradient id="boardGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{LINE}" stop-opacity=".16"/>
    <stop offset="100%" stop-color="{LINE}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{LINE}"/><stop offset="100%" stop-color="{CYAN}"/>
  </linearGradient>
  <filter id="tileGlow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="9"/>
  </filter>
  <pattern id="mesh" width="26" height="26" patternUnits="userSpaceOnUse">
    <circle cx="1.5" cy="1.5" r="1" fill="{LINE}" opacity=".12"/>
  </pattern>
</defs>

<rect width="1200" height="640" fill="{BG}"/>
<rect width="1200" height="640" fill="url(#mesh)"/>
<ellipse cx="300" cy="350" rx="380" ry="300" fill="url(#boardGlow)"/>

<g font-family="{MONO}">
  <text x="64" y="52" fill="{CYAN}" font-size="13" letter-spacing="4">03 &#183; FLAGSHIP &#183; 2048byNiklas</text>
  <text x="1136" y="52" fill="{DIM}" font-size="12" letter-spacing="2" text-anchor="end">REAL GAME &#183; SEED {game['seed']} &#183; NOT A MOCKUP</text>
  <line x1="64" y1="66" x2="1136" y2="66" stroke="{LINE}" stroke-opacity=".22"/>

  <rect x="64" y="120" width="472" height="472" rx="14" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".28"/>
  {cells}

  <rect x="600" y="120" width="536" height="160" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".28"/>
  <text x="640" y="162" fill="{DIM}" font-size="11" letter-spacing="2.6">SCORE</text>
  <text x="1096" y="162" fill="{DIM}" font-size="11" letter-spacing="2.6" text-anchor="end">LIVE REPLAY</text>
  <circle cx="1006" cy="158" r="3.4" fill="{CYAN}"><animate attributeName="opacity" values="1;.15;1" dur="1.4s" repeatCount="indefinite"/></circle>

  <rect x="600" y="296" width="536" height="78" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".28"/>
  <text x="640" y="320" fill="{DIM}" font-size="10.5" letter-spacing="2.2">MOVE</text>
  <text x="860" y="320" fill="{DIM}" font-size="10.5" letter-spacing="2.2">BEST TILE</text>
  <text x="1080" y="320" fill="{DIM}" font-size="10.5" letter-spacing="2.2" text-anchor="middle">DIR</text>

  <rect x="600" y="392" width="536" height="166" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-opacity=".28"/>
  {fact_rows}

  <text x="600" y="600" fill="{DIM}" font-size="12">full game &#183; {game['moves']:,} moves &#183; {game['score']:,} points &#183; {game['max_tile']:,} tile</text>
  <rect x="600" y="612" width="536" height="5" rx="2.5" fill="{GRID}"/>
  <rect x="600" y="612" width="0" height="5" rx="2.5" fill="url(#bar)">
    <animate attributeName="width" values="0;536" dur="{total:.2f}s" repeatCount="indefinite"/>
  </rect>

  <text x="64" y="614" fill="{DIM}" font-size="12">pure python &#183; standard library only &#183; no numpy, no c extension</text>

  {"".join(groups)}
</g>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--budget", type=float, default=300.0)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--frames", type=int, default=96)
    parser.add_argument("--frame-seconds", type=float, default=0.17)
    parser.add_argument("--hold", type=float, default=2.2)
    parser.add_argument("--save", type=Path, help="write the raw recording here for fast re-renders")
    args = parser.parse_args()

    game = json.loads(args.json.read_text()) if args.json else record(args.seed, args.budget)
    if args.save:
        args.save.write_text(json.dumps(game), encoding="utf-8")
    svg = render(game, args.frames, args.frame_seconds, args.hold)
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(OUT.parents[1])}: {game['moves']:,} moves, "
          f"score {game['score']:,}, best tile {game['max_tile']:,}, {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
