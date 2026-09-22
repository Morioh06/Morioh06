#!/usr/bin/env python3
"""Downsample a prepped grayscale photo to a character grid and emit a
self-typing monochrome ASCII SVG. Each row wipes in left-to-right with a
small block cursor riding the edge, staggered top to bottom; the whole
portrait prints once and freezes -- GitHub renders the SMIL animation
from a plain <img> tag.
"""
import sys
from xml.sax.saxutils import escape

from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears bg

COLS = 100
ROWS = 53
CHAR_W = 6
LINE_H = 11
PAD = 28
FONT_SIZE = 10
FILL = "#c9d1d9"
BG = "#0d1117"
ROW_DUR = 0.5
STAGGER = 0.045


def image_to_rows(path: str) -> list[str]:
    img = Image.open(path).convert("L").resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    n = len(RAMP) - 1
    rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            brightness = px[x, y]
            idx = round((255 - brightness) / 255 * n)
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    return rows


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W + PAD * 2
    height = ROWS * LINE_H + PAD * 2
    row_width = COLS * CHAR_W

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', Menlo, monospace" font-size="{FONT_SIZE}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{BG}"/>',
        "<defs>",
    ]

    for i in range(ROWS):
        parts.append(
            f'<clipPath id="row{i}"><rect x="0" y="0" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{row_width}" '
            f'dur="{ROW_DUR}s" begin="{i * STAGGER:.3f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f"</rect></clipPath>"
        )
    parts.append("</defs>")

    for i, row in enumerate(rows):
        y = PAD + i * LINE_H
        safe = escape(row)
        parts.append(
            f'<g clip-path="url(#row{i})" transform="translate({PAD},{y})">'
            f'<text x="0" y="{LINE_H - 2}" fill="{FILL}" textLength="{row_width}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{safe}</text>'
            f"</g>"
        )
        parts.append(
            f'<rect x="{PAD}" y="{y}" width="{CHAR_W}" height="{LINE_H}" fill="{FILL}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + row_width - CHAR_W}" '
            f'dur="{ROW_DUR}s" begin="{i * STAGGER:.3f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.85;1" '
            f'dur="{ROW_DUR}s" begin="{i * STAGGER:.3f}s" fill="freeze"/>'
            f"</rect>"
        )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "ascii-portrait.svg"
    grid_rows = image_to_rows(src)
    svg = build_svg(grid_rows)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out} ({COLS}x{ROWS} chars)")
