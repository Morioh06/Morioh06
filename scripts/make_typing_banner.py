#!/usr/bin/env python3
"""Two-line terminal intro banner: a prompt that types itself, then a
reply line that types in right after. Both freeze once printed; a small
cursor block keeps a slow, subtle infinite blink at the very end -- the
one place in this project that loops, since a resting terminal cursor
blinking forever is the realistic behavior, not a gimmick.
"""
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


def build_svg() -> str:
    height = PAD_Y * 2 + LINE_H * len(LINES)
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', Menlo, monospace" font-size="{FONT_SIZE}">',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
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
