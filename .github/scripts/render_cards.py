"""Draw the hand-authored story cards of the profile.

The cards share one typewriter engine and one CRT look, so the text lives in
one place instead of being hand-positioned inside four SVG files:

    assets/boot.svg    00 - power-on self test
    assets/flos.svg    02 - FLOS, the atomic Arch distribution
    assets/kernel.svg  03 - the from-scratch kernel
    assets/roblox.svg  05 - Roblox Studio

    python .github/scripts/render_cards.py

Standard library only.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "assets"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

DIM = "#6d5a8f"
BRIGHT = "#f2e8ff"
CYAN = "#22d3ee"
BG = "#07060b"
PANEL = "#0d0a17"

GREEN, AMBER, FAINT = "#7dffa4", "#ffb454", "#2f7a4a"
BLUE = "#5ac8fa"
RED = "#ff5252"


# ------------------------------------------------------------------ primitives

def chrome(width: int, height: int, index: str, title: str, right: str,
           accent: str = CYAN, bg: str = BG) -> str:
    """Card background, mesh, section header."""
    return f"""<rect width="{width}" height="{height}" fill="{bg}"/>
<rect width="{width}" height="{height}" fill="url(#mesh)"/>
<g font-family="{MONO}">
  <rect x="64" y="34" width="34" height="22" rx="5" fill="{accent}" opacity=".16"/>
  <text x="81" y="50" text-anchor="middle" fill="{accent}" font-size="12" font-weight="bold" letter-spacing="1">{index}</text>
  <text x="110" y="50" fill="{accent}" font-size="13" letter-spacing="4">{escape(title)}</text>
  <text x="{width - 64}" y="50" fill="{DIM}" font-size="12" letter-spacing="2" text-anchor="end">{escape(right)}</text>
  <line x1="64" y1="66" x2="{width - 64}" y2="66" stroke="{accent}" stroke-opacity=".22"/>
</g>"""


def defs(accent: str, extra: str = "") -> str:
    return f"""<defs>
  <pattern id="mesh" width="26" height="26" patternUnits="userSpaceOnUse">
    <circle cx="1.5" cy="1.5" r="1" fill="{accent}" opacity=".12"/>
  </pattern>
  <pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="1" fill="#ffffff" opacity=".05"/>
  </pattern>
  <radialGradient id="vignette" cx="50%" cy="50%" r="72%">
    <stop offset="55%" stop-color="#000000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000000" stop-opacity=".62"/>
  </radialGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{accent}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{accent}" stop-opacity=".9"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </linearGradient>
  <filter id="phosphor" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
{extra}</defs>"""


def crt_overlay(width: int, height: int, tint: str) -> str:
    return f"""<rect width="{width}" height="{height}" fill="url(#scan)"/>
<rect width="{width}" height="{height}" fill="url(#vignette)"/>
<rect x="0" y="-80" width="{width}" height="80" fill="{tint}" opacity=".05" filter="url(#soft)">
  <animate attributeName="y" values="-80;{height}" dur="7s" repeatCount="indefinite"/>
</rect>"""


def sublabel(x: float, y: float, text: str, colour: str = DIM) -> str:
    return f'  <text x="{x}" y="{y}" fill="{colour}" font-size="11" letter-spacing="2.6">{escape(text)}</text>'


class Typer:
    """Lines that type themselves, then reset together. One shared clock."""

    def __init__(self, total: float, font: float, cursor: str):
        self.total = total
        self.font = font
        self.advance = font * 0.6
        self.cursor = cursor
        self.clips: list[str] = []
        self.body: list[str] = []
        self._n = 0

    def line(self, x: float, y: float, spans: list[tuple[str, str]], begin: float,
             speed: float = 0.022, cursor: bool = True) -> float:
        plain = "".join(text for text, _ in spans)
        if not plain.strip():
            return begin
        width = len(plain) * self.advance
        dur = max(0.12, len(plain) * speed)
        self._n += 1
        cid = f"c{self._n}"
        t = self.total

        keys = f"0;{begin / t:.5f};{(begin + dur) / t:.5f};.965;.972;1"
        self.clips.append(
            f'  <clipPath id="{cid}"><rect x="{x - 4}" y="{y - self.font}" '
            f'width="0" height="{self.font * 1.5:.0f}">'
            f'<animate attributeName="width" values="0;0;{width + 6:.0f};{width + 6:.0f};0;0" '
            f'keyTimes="{keys}" dur="{t:.2f}s" repeatCount="indefinite"/></rect></clipPath>')

        tspans = "".join(
            f'<tspan fill="{colour}">{escape(text).replace(" ", "&#160;")}</tspan>'
            for text, colour in spans)
        self.body.append(
            f'  <g clip-path="url(#{cid})"><text x="{x}" y="{y}" font-size="{self.font}" '
            f'textLength="{width:.0f}" lengthAdjust="spacing" xml:space="preserve">{tspans}</text></g>')

        if cursor:
            self.body.append(
                f'  <rect x="{x}" y="{y - self.font * 0.82:.0f}" width="{self.advance:.1f}" '
                f'height="{self.font:.0f}" fill="{self.cursor}" opacity="0">'
                f'<animate attributeName="x" values="{x};{x};{x + width:.0f};{x + width:.0f};{x};{x}" '
                f'keyTimes="{keys}" dur="{t:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="0;{begin / t:.5f};{(begin + 0.01) / t:.5f};'
                f'{(begin + dur + 0.12) / t:.5f};{(begin + dur + 0.13) / t:.5f};1" '
                f'dur="{t:.2f}s" repeatCount="indefinite"/></rect>')
        return begin + dur

    def idle_cursor(self, x: float, y: float, begin: float) -> str:
        t = self.total
        return (f'  <g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="0;{begin / t:.5f};{(begin + 0.01) / t:.5f};.965;.972;1" '
                f'dur="{t:.2f}s" repeatCount="indefinite"/>'
                f'<rect x="{x}" y="{y - self.font * 0.82:.0f}" width="{self.advance:.1f}" '
                f'height="{self.font:.0f}" fill="{self.cursor}">'
                f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/>'
                f'</rect></g>')


def svg(width: int, height: int, label: str, defs_block: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-label="{escape(label)}">\n'
            f'<title>{escape(label)}</title>\n{defs_block}\n{body}\n</svg>\n')


# ------------------------------------------------------------------- 00 - POST

def render_boot() -> str:
    W, H = 1200, 560
    SCREEN = "#040806"

    T = 14.0
    t = Typer(total=T, font=16, cursor=GREEN)
    x, y, lh = 112, 150, 27
    at = 0.3

    def row(spans, **kw):
        nonlocal y, at
        at = t.line(x, y, spans, at, **kw) + 0.06
        y += lh

    def blank():
        nonlocal y
        y += lh * 0.45

    row([("NUKLASO BIOS v2.0", AMBER), ("   profile power-on self test", FAINT)], speed=.016)
    row([("--------------------------------------------------------", FAINT)], speed=.004, cursor=False)
    blank()
    row([("cpu   ", GREEN), ("niklas, regensburg de ................. ", FAINT), ("[ OK ]", AMBER)], speed=.012)
    row([("mem   ", GREEN), ("caffeine, curiosity, spare evenings .... ", FAINT), ("[ OK ]", AMBER)], speed=.012)
    row([("disp  ", GREEN), ("1200px of svg, zero javascript ........ ", FAINT), ("[ OK ]", AMBER)], speed=.012)
    blank()
    row([("scanning attached subsystems ...", GREEN)], speed=.014)
    blank()
    row([(" 0x01  ", FAINT), ("flos     ", "#ffffff"), ("distro    ", GREEN), ("atomic arch + plasma  ", FAINT), ("PRE-RELEASE", AMBER)], speed=.008)
    row([(" 0x02  ", FAINT), ("kernel   ", "#ffffff"), ("bare metal", GREEN), ("c + x86_64 asm        ", FAINT), ("BOOTING    ", AMBER)], speed=.008)
    row([(" 0x03  ", FAINT), ("roblox   ", "#ffffff"), ("game dev  ", GREEN), ("luau, live systems    ", FAINT), ("ONLINE     ", AMBER)], speed=.008)
    row([(" 0x04  ", FAINT), ("2048     ", "#ffffff"), ("solver    ", GREEN), ("expectimax, python    ", FAINT), ("ONLINE     ", AMBER)], speed=.008)
    blank()
    row([("4 subsystems found. handing control to the profile.", GREEN)], speed=.012, cursor=False)

    body = [
        chrome(W, H, "00", "POWER-ON SELF TEST", "PRESS ANY KEY · OR JUST SCROLL", GREEN, SCREEN),
        f'  <rect x="64" y="96" width="{W - 128}" height="{H - 152}" rx="10" fill="#020403" stroke="{FAINT}" stroke-opacity=".5"/>',
        f'  <rect x="84" y="96" width="{W - 168}" height="2" fill="url(#edge)">'
        f'<animate attributeName="opacity" values=".3;1;.3" dur="3.2s" repeatCount="indefinite"/></rect>',
        f'<g font-family="{MONO}" filter="url(#phosphor)">',
        "\n".join(t.body),
        t.idle_cursor(x, y + 4, at + 0.3),
        "</g>",
        crt_overlay(W, H, GREEN),
        f'  <rect width="{W}" height="{H}" fill="{GREEN}" opacity="0">'
        f'<animate attributeName="opacity" values="0;.035;0;0;.02;0" dur="5.7s" repeatCount="indefinite"/></rect>',
    ]
    return svg(W, H, "power-on self test", defs(GREEN, "".join(c + "\n" for c in t.clips)), "\n".join(body))


# --------------------------------------------------------------------- 02 FLOS

SPEC = [
    ("RELEASE", "26.10 “Amaryllis”"),
    ("BASE", "Arch · Btrfs · signed UKI"),
    ("DESKTOP", "KDE Plasma 6.7 · Wayland only"),
    ("TARGET", "x86_64 UEFI · Secure Boot"),
    ("GAMING", "Steam · gamescope · GameMode · MangoHud"),
    ("SECURITY", "FDE · AppArmor · firewalld · all signed"),
]

FLOW = [("01", "build"), ("02", "sign"), ("03", "commit"), ("04", "reboot")]

STATUS = [
    ("0", "ISO IMAGES", "across nine build runs"),
    ("1 / 8", "MILESTONES", "under way, none complete"),
    ("24", "PACKAGES", "built from source"),
    ("5 + 1", "DEPLOYMENTS", "kept, plus factory snapshot"),
]


def render_flos() -> str:
    W, H = 1200, 612
    body = [chrome(W, H, "02", "FLOS", "FLO-OS.DE · PRE-RELEASE", BLUE, "#05080c")]

    body.append(f'  <rect x="64" y="96" width="536" height="448" rx="12" fill="{PANEL}" stroke="{BLUE}" stroke-opacity=".26"/>')
    body.append(f'  <rect x="86" y="96" width="492" height="2" fill="url(#edge)">'
                f'<animate attributeName="opacity" values=".25;1;.25" dur="3.4s" repeatCount="indefinite"/></rect>')
    body.append(f'<g font-family="{MONO}">')
    body.append(sublabel(92, 128, "SPECIFICATION"))
    body.append(f'  <text x="92" y="166" fill="{BRIGHT}" font-size="20" font-weight="bold">Linux in full bloom</text>')
    body.append(f'  <text x="92" y="190" fill="#9fc3d6" font-size="12.5">a gaming-ready, atomic KDE Plasma Wayland distribution on Arch</text>')

    for i, (label, value) in enumerate(SPEC):
        ry = 228 + i * 34
        body.append(f'  <text x="92" y="{ry}" fill="{DIM}" font-size="11.5" letter-spacing="1.4">{escape(label)}</text>')
        body.append(f'  <text x="572" y="{ry}" text-anchor="end" fill="#cfe3ee" font-size="12.5">{escape(value)}</text>')
        body.append(f'  <line x1="92" y1="{ry + 10}" x2="572" y2="{ry + 10}" stroke="{BLUE}" stroke-opacity=".1"/>')

    body.append(sublabel(92, 464, "HOW AN UPDATE LANDS · ATOMIC, OR NOT AT ALL"))
    for i, (num, name) in enumerate(FLOW):
        cx = 92 + i * 122
        body.append(f'  <rect x="{cx}" y="482" width="110" height="46" rx="8" fill="#0a1218" stroke="{BLUE}" stroke-opacity=".3"/>')
        body.append(f'  <text x="{cx + 12}" y="502" fill="{BLUE}" font-size="10.5" letter-spacing="1.4">{num}</text>')
        body.append(f'  <text x="{cx + 12}" y="519" fill="{BRIGHT}" font-size="13">{name}</text>')
        if i < len(FLOW) - 1:
            body.append(f'  <path d="M{cx + 112},505 L{cx + 120},505" stroke="{BLUE}" stroke-opacity=".45" stroke-width="1.4"/>')
    body.append(f'  <circle r="3.4" fill="{BLUE}"><animateMotion dur="4.2s" repeatCount="indefinite" '
                f'path="M98,474 L568,474"/><animate attributeName="opacity" values="0;1;1;0" dur="4.2s" repeatCount="indefinite"/></circle>')

    body.append(f'  <rect x="636" y="96" width="500" height="448" rx="12" fill="{PANEL}" stroke="{BLUE}" stroke-opacity=".26"/>')
    body.append(sublabel(664, 128, "WHERE FLOS ACTUALLY IS"))
    body.append(f'  <rect x="664" y="146" width="444" height="48" rx="8" fill="{AMBER}" opacity=".12"/>')
    body.append(f'  <circle cx="688" cy="170" r="4" fill="{AMBER}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    body.append(f'  <text x="704" y="175" fill="{AMBER}" font-size="13.5" letter-spacing="1.2">PRE-RELEASE — NOTHING HAS BOOTED YET</text>')

    for i, (value, label, note) in enumerate(STATUS):
        tx = 664 + (i % 2) * 228
        ty = 216 + (i // 2) * 124
        body.append(f'  <rect x="{tx}" y="{ty}" width="216" height="110" rx="10" fill="#0a1218" stroke="{BLUE}" stroke-opacity=".22"/>')
        body.append(f'  <text x="{tx + 20}" y="{ty + 56}" fill="{BLUE}" font-size="34" font-weight="bold">{escape(value)}</text>')
        body.append(f'  <text x="{tx + 20}" y="{ty + 78}" fill="{BRIGHT}" font-size="11" letter-spacing="1.6">{escape(label)}</text>')
        body.append(f'  <text x="{tx + 20}" y="{ty + 96}" fill="{DIM}" font-size="10.5">{escape(note)}</text>')

    body.append(f'  <text x="664" y="500" fill="#7f93a3" font-size="12">the site tracks what is specified against what has actually run,</text>')
    body.append(f'  <text x="664" y="520" fill="#7f93a3" font-size="12">and says on its own front page that the second column is empty.</text>')
    body.append(f'  <text x="64" y="580" fill="{BLUE}" font-size="13" letter-spacing="1.6">flo-os.de</text>')
    body.append(f'  <text x="1136" y="580" text-anchor="end" fill="{DIM}" font-size="11.5">no telemetry · no accounts · no cloud dependency</text>')
    body.append("</g>")
    body.append(crt_overlay(W, H, BLUE))

    return svg(W, H, "FLOS - an atomic Arch distribution", defs(BLUE), "\n".join(body))


# ------------------------------------------------------------------- 03 KERNEL

ROADMAP = [
    ("bootloader", "stage1 loads and jumps to the kernel", "DONE"),
    ("vga text output", "write to 0xB8000, then a real console", "NEXT"),
    ("gdt / idt", "descriptor tables and interrupt handlers", "PLANNED"),
    ("keyboard", "ps/2 driver, scancodes to characters", "PLANNED"),
    ("memory", "physical allocator, then paging", "PLANNED"),
    ("scheduler", "tasks, context switching, timers", "PLANNED"),
]

STATE = {"DONE": (GREEN, ".9"), "NEXT": (AMBER, ".8"), "PLANNED": (DIM, ".5")}


def render_kernel() -> str:
    W, H = 1200, 660

    T = 11.0
    t = Typer(total=T, font=15, cursor=GREEN)
    x, y, lh = 104, 178, 26
    at = 0.3

    at = t.line(x, y, [("$ ", FAINT), ("qemu-system-x86_64 -drive format=raw,file=flo.img", "#e6ffe9")], at, speed=.016)
    y += lh + lh * 0.5
    at = t.line(x, y, [("Booting ...", GREEN)], at + .25, speed=.02)
    y += lh
    at = t.line(x, y, [("[ ok ] ", AMBER), ("stage1 handed control to the kernel entry", FAINT)], at + .2, speed=.012)
    y += lh + lh * 0.5
    at = t.line(x, y, [("everything under this line is still being written.", FAINT)], at + .3, speed=.012)
    y += lh
    at = t.line(x, y, [("that is the whole point.", "#e6ffe9")], at + .2, speed=.02)
    y += lh

    rows = []
    done = sum(1 for _, _, s in ROADMAP if s == "DONE")
    for i, (name, note, state) in enumerate(ROADMAP):
        ry = 150 + i * 74
        colour, op = STATE[state]
        rows.append(f"""  <g>
    <rect x="636" y="{ry}" width="500" height="60" rx="9" fill="{PANEL}" stroke="{colour}" stroke-opacity="{op}"/>
    <rect x="636" y="{ry}" width="4" height="60" rx="2" fill="{colour}" opacity="{op}"/>
    <text x="660" y="{ry + 26}" fill="{BRIGHT}" font-size="14" font-weight="bold">{escape(name)}</text>
    <text x="660" y="{ry + 46}" fill="{DIM}" font-size="12">{escape(note)}</text>
    <rect x="1030" y="{ry + 16}" width="88" height="24" rx="12" fill="{colour}" opacity=".14"/>
    <text x="1074" y="{ry + 32}" text-anchor="middle" fill="{colour}" font-size="10.5" letter-spacing="1.4">{state}</text>
  </g>""")

    body = [
        chrome(W, H, "03", "THE KERNEL", "C + x86_64 ASM · QEMU · NO BASE DISTRO", GREEN, "#050705"),
        f'  <rect x="64" y="96" width="536" height="{H - 160}" rx="10" fill="#020403" stroke="{FAINT}" stroke-opacity=".5"/>',
        f'  <path d="M76,96 H588 a10,10 0 0 1 10,10 V130 H64 V106 a10,10 0 0 1 12,-10 Z" fill="#0a140d"/>',
        f'  <line x1="64" y1="130" x2="600" y2="130" stroke="{FAINT}" stroke-opacity=".6"/>',
        f'  <circle cx="88" cy="113" r="5" fill="#ff5f57"/><circle cx="106" cy="113" r="5" fill="#febc2e"/><circle cx="124" cy="113" r="5" fill="#28c840"/>',
        f'  <text x="332" y="118" text-anchor="middle" fill="{FAINT}" font-size="11.5" font-family="{MONO}" letter-spacing="1.2">QEMU — flo.img</text>',
        f'<g font-family="{MONO}" filter="url(#phosphor)">',
        "\n".join(t.body),
        t.idle_cursor(x, y, at + 0.3),
        "</g>",
        f'<g font-family="{MONO}">',
        f'  <text x="636" y="118" fill="{DIM}" font-size="11" letter-spacing="2.6">SUBSYSTEM ROADMAP</text>',
        f'  <text x="1136" y="118" text-anchor="end" fill="{DIM}" font-size="11" letter-spacing="1.6">{done} OF {len(ROADMAP)}</text>',
        "\n".join(rows),
        f'  <rect x="636" y="{150 + len(ROADMAP) * 74 + 12}" width="500" height="5" rx="2.5" fill="#1d1630"/>',
        f'  <rect x="636" y="{150 + len(ROADMAP) * 74 + 12}" width="0" height="5" rx="2.5" fill="{GREEN}">'
        f'<animate attributeName="width" from="0" to="{500 * done / len(ROADMAP):.0f}" dur="1.2s" fill="freeze"/></rect>',
        f'  <text x="104" y="{H - 34}" fill="{FAINT}" font-size="12">no fork, no base distro - this one starts at the boot sector</text>',
        "</g>",
        crt_overlay(W, H, GREEN),
    ]
    return svg(W, H, "a kernel written from scratch", defs(GREEN, "".join(c + "\n" for c in t.clips)), "\n".join(body))


# ------------------------------------------------------------------- 05 ROBLOX

def render_roblox() -> str:
    W, H = 1200, 600
    WHITE, GREY = "#f6f7f9", "#8b93a7"
    EDITOR = "#12141a"
    KEY, STR, FN, VAR, COM = "#ff7b72", "#a5d6ff", "#d2a8ff", "#e6edf3", "#6e7a8a"

    T = 14.0
    t = Typer(total=T, font=14.5, cursor=RED)
    x, y, lh = 112, 168, 25
    at = 0.3

    code = [
        [("-- ServerScriptService/Economy.server.luau", COM)],
        [("local", KEY), (" Players ", VAR), ("= ", VAR), ("game", FN), (":GetService(", VAR), ('"Players"', STR), (")", VAR)],
        [("local", KEY), (" Store ", VAR), ("= ", VAR), ("require(script.Parent.Profile)", VAR)],
        [],
        [("Players.PlayerAdded:Connect(", VAR), ("function", KEY), ("(player)", VAR)],
        [("    local", KEY), (" profile ", VAR), ("= Store.load(player.UserId)", VAR)],
        [("    player:SetAttribute(", VAR), ('"Coins"', STR), (", profile.coins)", VAR)],
        [("    profile.sessions ", VAR), ("+= ", KEY), ("1", STR)],
        [("    Store.save(player.UserId, profile)", VAR)],
        [("end)", VAR)],
    ]

    line_ys: list[float] = []
    for spans in code:
        if not spans:
            y += lh * 0.5
            continue
        at = t.line(x, y, spans, at + .12, speed=.014)
        line_ys.append(y)
        y += lh

    ox, oy, tw, th = 900, 330, 46, 23
    plate = []
    for r in range(4):
        for c in range(4):
            px = ox + (c - r) * tw
            py = oy + (c + r) * th
            plate.append(f'<path d="M{px},{py} l{tw},{th} l{-tw},{th} l{-tw},{-th} Z" '
                         f'fill="#1c2030" stroke="#2c3245" stroke-width="1"/>')

    parts = []
    for i, (c, r, hgt, colour) in enumerate([(1, 1, 34, RED), (2, 0, 24, AMBER),
                                             (0, 2, 44, BLUE), (3, 2, 28, "#b388ff")]):
        px = ox + (c - r) * tw
        py = oy + (c + r) * th
        pop = 0.30 + i * 0.09
        parts.append(f"""<g opacity="0">
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{pop:.3f};{pop + 0.04:.3f};.93;.95;1" dur="{T}s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="translate" values="0 -26;0 -26;0 0;0 0" keyTimes="0;{pop:.3f};{pop + 0.035:.3f};1" dur="{T}s" repeatCount="indefinite"/>
      <path d="M{px},{py - hgt} l{tw},{th} l0,{hgt} l{-tw},{-th} Z" fill="{colour}" opacity=".55"/>
      <path d="M{px},{py - hgt} l{-tw},{th} l0,{hgt} l{tw},{-th} Z" fill="{colour}" opacity=".35"/>
      <path d="M{px},{py - hgt - th} l{tw},{th} l{-tw},{th} l{-tw},{-th} Z" fill="{colour}"/>
    </g>""")

    tree = [("Workspace", WHITE), ("  Baseplate", GREY), ("  SpawnLocation", GREY),
            ("ServerScriptService", WHITE), ("  Economy", RED), ("  Profile", GREY),
            ("ReplicatedStorage", WHITE), ("  Remotes", GREY)]
    tree_rows = "".join(
        f'<text x="676" y="{136 + i * 22}" fill="{colour}" font-size="12">{escape(name)}</text>'
        for i, (name, colour) in enumerate(tree))

    body = [
        chrome(W, H, "05", "ROBLOX STUDIO", "LUAU · GAME SYSTEMS · LIVE PLAYERS", RED, "#080a10"),
        f'  <rect x="64" y="96" width="556" height="{H - 160}" rx="10" fill="{EDITOR}" stroke="{RED}" stroke-opacity=".3"/>',
        f'  <path d="M76,96 H608 a10,10 0 0 1 10,10 V128 H64 V106 a10,10 0 0 1 12,-10 Z" fill="#1b1e26"/>',
        f'  <line x1="64" y1="128" x2="620" y2="128" stroke="{RED}" stroke-opacity=".26"/>',
        f'  <rect x="80" y="104" width="150" height="24" rx="5" fill="{EDITOR}"/>',
        f'  <text x="92" y="121" fill="{GREY}" font-size="11.5" font-family="{MONO}">Economy.luau</text>',
        f'  <text x="600" y="121" text-anchor="end" fill="{GREY}" font-size="11" font-family="{MONO}">SERVER</text>',
        f'<g font-family="{MONO}">',
        "\n".join(f'  <text x="86" y="{ly:.0f}" fill="#39404f" font-size="12" text-anchor="end">{i + 1}</text>'
                  for i, ly in enumerate(line_ys)),
        "\n".join(t.body),
        t.idle_cursor(x, y, at + 0.3),
        "</g>",
        f'<g font-family="{MONO}">',
        f'  <rect x="652" y="96" width="484" height="{H - 160}" rx="10" fill="#0d1017" stroke="{RED}" stroke-opacity=".22"/>',
        sublabel(676, 116, "EXPLORER", GREY),
        f'  {tree_rows}',
        f'  <line x1="676" y1="{136 + len(tree) * 22 + 6}" x2="1112" y2="{136 + len(tree) * 22 + 6}" stroke="{RED}" stroke-opacity=".18"/>',
        "".join(plate),
        "".join(parts),
        f'  <text x="894" y="{H - 122}" text-anchor="middle" fill="{GREY}" font-size="11.5" letter-spacing="1.6">instancing parts at runtime</text>',
        "</g>",
        f'<g font-family="{MONO}">'
        f'<text x="112" y="{H - 34}" fill="{GREY}" font-size="12">server authority, data that survives a rejoin, and UI that does not fight the player</text></g>',
        crt_overlay(W, H, RED),
    ]
    return svg(W, H, "Roblox Studio - Luau game systems", defs(RED, "".join(c + "\n" for c in t.clips)), "\n".join(body))


# ------------------------------------------------------------------------- main

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, markup in {
        "boot.svg": render_boot(),
        "flos.svg": render_flos(),
        "kernel.svg": render_kernel(),
        "roblox.svg": render_roblox(),
    }.items():
        (OUT / name).write_text(markup, encoding="utf-8", newline="\n")
        print(f"wrote assets/{name}  ({len(markup) // 1024} KB)")


if __name__ == "__main__":
    main()
