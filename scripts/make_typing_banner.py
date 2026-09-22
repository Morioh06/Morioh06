#!/usr/bin/env python3
"""Two-line terminal intro banner: a prompt that types itself, then a
reply line that types in right after. Both freeze once printed; a small
cursor block keeps a slow, subtle infinite blink at the very end, and a
dim Matrix-rain drizzle runs behind everything -- the two intentionally
looping touches in this project, since a resting cursor and background
rain are meant to run forever, not freeze.
"""
import random
import sys
from xml.sax.saxutils import escape

LINES = [
    ('$ ', "whoami"),
    ("", 'Jesus -- Estudiante ITC @ TNM, construyendo con Python, SQL, C#, JS'),
]

WIDTH = 860
PAD_X = 24
PAD_Y = 20
LINE_H = 30
FONT_SIZE = 16
CHAR_W = FONT_SIZE * 0.6
FILL = "#c9d1d9"
PROMPT_COLOR = "#7ee787"
BG = "#0d1117"
BORDER = "#30363d"
ROW_DUR = 0.55
ROW_GAP = 0.15

RAIN_CHARS = "0123456789ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
RAIN_COLOR = "#39d353"
RAIN_COL_W = 16
RAIN_FONT_SIZE = 13
RAIN_TRAIL_LEN = 6
RAIN_TRAIL_GAP = 15
RAIN_SEED = 42


def build_matrix_rain(width: int, height: int) -> str:
    rng = random.Random(RAIN_SEED)
    n_cols = width // RAIN_COL_W
    trail_h = RAIN_TRAIL_LEN * RAIN_TRAIL_GAP

    columns = []
    for c in range(n_cols):
        x = c * RAIN_COL_W + RAIN_COL_W / 2
        chars = [rng.choice(RAIN_CHARS) for _ in range(RAIN_TRAIL_LEN)]
        tspans = "".join(
            f'<tspan x="{x}" dy="{0 if j == 0 else RAIN_TRAIL_GAP}" '
            f'opacity="{0.08 + 0.75 * (j / (RAIN_TRAIL_LEN - 1)) ** 2:.2f}">{ch}</tspan>'
            for j, ch in enumerate(chars)
        )
        dur = rng.uniform(2.2, 4.5)
        begin = rng.uniform(-dur, 0)
        columns.append(
            f'<g transform="translate(0,{-trail_h})">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 {-trail_h}" to="0 {height}" dur="{dur:.2f}s" begin="{begin:.2f}s" '
            f'repeatCount="indefinite"/>'
            f'<text x="0" y="0" font-size="{RAIN_FONT_SIZE}" fill="{RAIN_COLOR}" '
            f'text-anchor="middle">{tspans}</text></g>'
        )

    return (
        f'<g clip-path="url(#cardclip)" opacity="0.55">{"".join(columns)}</g>'
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{BG}" opacity="0.5"/>'
    )


def build_svg() -> str:
    height = PAD_Y * 2 + LINE_H * len(LINES)
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', Menlo, monospace" font-size="{FONT_SIZE}">',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<clipPath id="cardclip"><rect x="0" y="0" width="{WIDTH}" height="{height}" rx="14"/></clipPath>',
        build_matrix_rain(WIDTH, height),
        "<defs>",
    ]

    row_end_x = []
    for i, (prompt, text) in enumerate(LINES):
        full = prompt + text
        row_width = len(full) * CHAR_W
        row_end_x.append(PAD_X + row_width)
        begin = i * (ROW_DUR + ROW_GAP)
        parts.append(
            f'<clipPath id="line{i}"><rect x="0" y="0" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{row_width}" dur="{ROW_DUR}s" '
            f'begin="{begin:.3f}s" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f"</rect></clipPath>"
        )
    parts.append("</defs>")

    for i, (prompt, text) in enumerate(LINES):
        y = PAD_Y + i * LINE_H
        full = prompt + text
        row_width = len(full) * CHAR_W
        parts.append(
            f'<g clip-path="url(#line{i})" transform="translate({PAD_X},{y})">'
            f'<text x="0" y="{LINE_H - 10}" xml:space="preserve">'
            f'<tspan fill="{PROMPT_COLOR}" font-weight="700">{escape(prompt)}</tspan>'
            f'<tspan fill="{FILL}">{escape(text)}</tspan>'
            f"</text></g>"
        )

    last_i = len(LINES) - 1
    cursor_x = row_end_x[last_i]
    cursor_y = PAD_Y + last_i * LINE_H
    cursor_appear = last_i * (ROW_DUR + ROW_GAP) + ROW_DUR
    parts.append(
        f'<rect x="{cursor_x:.1f}" y="{cursor_y}" width="{CHAR_W:.1f}" height="{LINE_H - 10}" '
        f'fill="{FILL}" opacity="0">'
        f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" '
        f'dur="1.1s" begin="{cursor_appear:.3f}s" repeatCount="indefinite"/>'
        f"</rect>"
    )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "typing-banner.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print(f"Wrote {out}")
