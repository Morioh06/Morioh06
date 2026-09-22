#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG: a title bar, a few
key/value rows that fade and slide in on a short stagger, and a classic
neofetch color-swatch strip at the bottom for flavor. Set STATIC=1 to
emit a frozen frame (final state, no animation) for local Quick Look
previews.
"""
import os
import sys
from xml.sax.saxutils import escape

USERNAME = "morioh06"

ROWS = [
    ("Now", "Estudiante ITC @ TNM (2024-2026, en curso)"),
    ("Stack", "Python · SQL · JS · C# · Bash/PowerShell"),
    ("Highlights", "Slotly"),
]

KEY_COLORS = ["#ff7b72", "#d2a8ff", "#7ee787"]
VALUE_COLOR = "#c9d1d9"
BG = "#0d1117"
TITLEBAR_BG = "#161b22"
BORDER = "#30363d"

WIDTH = 490
PAD_X = 22
LABEL_W = 116
TITLEBAR_H = 34
ROW_H = 38
PAD_TOP = 20
PAD_BOTTOM = 20
ROW_FONT_SIZE = 12

SWATCH_SIZE = 16
SWATCH_GAP = 5
SWATCH_ROW_GAP = 6
SWATCH_TOP_MARGIN = 18
DIVIDER_MARGIN = 10

# classic ANSI 16-color terminal palette (normal row, then bright row)
PALETTE_NORMAL = ["#484f58", "#ff7b72", "#7ee787", "#d29922", "#79c0ff", "#d2a8ff", "#39c5cf", "#c9d1d9"]
PALETTE_BRIGHT = ["#6e7681", "#ffa198", "#56d364", "#e3b341", "#a5d6ff", "#e2c5ff", "#56d4dd", "#f0f6fc"]

STATIC = os.environ.get("STATIC") == "1"


def fade_in(begin: float) -> tuple[str, str]:
    if STATIC:
        return "", ""
    attrs = ' transform="translate(0,8)" opacity="0"'
    anim = (
        f'<animate attributeName="opacity" from="0" to="1" dur="0.45s" '
        f'begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 8" to="0 0" dur="0.45s" begin="{begin:.2f}s" fill="freeze" '
        f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
    )
    return attrs, anim


def row_block(i: int, key: str, value: str) -> str:
    y = TITLEBAR_H + PAD_TOP + i * ROW_H
    key_color = KEY_COLORS[i % len(KEY_COLORS)]
    attrs, anim = fade_in(0.5 + i * 0.15)
    return (
        f"<g{attrs}>"
        f"{anim}"
        f'<text x="{PAD_X}" y="{y}" font-size="{ROW_FONT_SIZE}" font-weight="700" '
        f'fill="{key_color}">{escape(key)}:</text>'
        f'<text x="{PAD_X + LABEL_W}" y="{y}" font-size="{ROW_FONT_SIZE}" '
        f'fill="{VALUE_COLOR}">{escape(value)}</text>'
        f"</g>"
    )


def swatch_row(y: float, colors: list[str], row_index: int, base_begin: float) -> str:
    parts = []
    for i, color in enumerate(colors):
        x = PAD_X + i * (SWATCH_SIZE + SWATCH_GAP)
        begin = base_begin + (row_index * len(colors) + i) * 0.025
        attrs, anim = fade_in(begin)
        parts.append(
            f'<g{attrs}>{anim}<rect x="{x}" y="{y}" width="{SWATCH_SIZE}" '
            f'height="{SWATCH_SIZE}" rx="3" fill="{color}"/></g>'
        )
    return "".join(parts)


def build_svg() -> str:
    rows_bottom = TITLEBAR_H + PAD_TOP + len(ROWS) * ROW_H
    divider_y = rows_bottom - ROW_H + 24 + DIVIDER_MARGIN
    swatch_top = divider_y + SWATCH_TOP_MARGIN
    height = swatch_top + SWATCH_SIZE * 2 + SWATCH_ROW_GAP + PAD_BOTTOM
    mid_y = TITLEBAR_H / 2

    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', Menlo, monospace">',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="14" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<path d="M0.5,{TITLEBAR_H} L0.5,14.5 Q0.5,0.5 14.5,0.5 L{WIDTH - 14.5},0.5 '
        f'Q{WIDTH - 0.5},0.5 {WIDTH - 0.5},14.5 L{WIDTH - 0.5},{TITLEBAR_H} Z" fill="{TITLEBAR_BG}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" stroke="{BORDER}"/>',
        f'<circle cx="24" cy="{mid_y}" r="6" fill="#ff5f56"/>',
        f'<circle cx="44" cy="{mid_y}" r="6" fill="#ffbd2e"/>',
        f'<circle cx="64" cy="{mid_y}" r="6" fill="#27c93f"/>',
        f'<text x="{WIDTH / 2}" y="{mid_y + 4}" text-anchor="middle" '
        f'fill="{VALUE_COLOR}" font-size="12">{escape(USERNAME)}@github</text>',
    ]
    for i, (key, value) in enumerate(ROWS):
        parts.append(row_block(i, key, value))

    parts.append(f'<line x1="{PAD_X}" y1="{divider_y}" x2="{WIDTH - PAD_X}" y2="{divider_y}" stroke="{BORDER}"/>')

    swatch_begin = 0.5 + len(ROWS) * 0.15 + 0.2
    parts.append(swatch_row(swatch_top, PALETTE_NORMAL, 0, swatch_begin))
    parts.append(swatch_row(swatch_top + SWATCH_SIZE + SWATCH_ROW_GAP, PALETTE_BRIGHT, 1, swatch_begin))

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print(f"Wrote {out}{' (static)' if STATIC else ''}")
