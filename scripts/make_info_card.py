#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG: a title bar plus a few
key/value rows that fade and slide in on a short stagger, as if the
panel is printing next to the ASCII portrait. Set STATIC=1 to emit a
frozen frame (final state, no animation) for local Quick Look previews.
"""
import os
import sys
from xml.sax.saxutils import escape

USERNAME = "morioh06"

ROWS = [
    ("Now", "Estudiante ITC @ TNM (Ago-Dic 2026)"),
    ("Prev", "BD · Circuitos · Mate Aplicada"),
    ("Stack", "Python · SQL · JS · Bash/PowerShell"),
    ("Highlights", "Citas Médicas (BDD 3FN) · vault con IA"),
]

KEY_COLORS = ["#ff7b72", "#79c0ff", "#d2a8ff", "#7ee787"]
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
PAD_BOTTOM = 18
ROW_FONT_SIZE = 12

STATIC = os.environ.get("STATIC") == "1"


def row_block(i: int, key: str, value: str) -> str:
    y = TITLEBAR_H + PAD_TOP + i * ROW_H
    key_color = KEY_COLORS[i % len(KEY_COLORS)]
    begin = 0.5 + i * 0.15
    if STATIC:
        group_attrs = ""
        anim = ""
    else:
        group_attrs = ' transform="translate(0,8)" opacity="0"'
        anim = (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.45s" '
            f'begin="{begin:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 8" to="0 0" dur="0.45s" begin="{begin:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
        )
    return (
        f"<g{group_attrs}>"
        f"{anim}"
        f'<text x="{PAD_X}" y="{y}" font-size="{ROW_FONT_SIZE}" font-weight="700" '
        f'fill="{key_color}">{escape(key)}:</text>'
        f'<text x="{PAD_X + LABEL_W}" y="{y}" font-size="{ROW_FONT_SIZE}" '
        f'fill="{VALUE_COLOR}">{escape(value)}</text>'
        f"</g>"
    )


def build_svg() -> str:
    height = TITLEBAR_H + PAD_TOP + len(ROWS) * ROW_H + PAD_BOTTOM
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
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print(f"Wrote {out}{' (static)' if STATIC else ''}")
