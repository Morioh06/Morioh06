#!/usr/bin/env python3
"""Stacked language-usage bar, GitHub-repo-page style. Percentages here
are a manual estimate of the Stack row (not scraped from the GitHub API):
with a single, brand-new public repo the real per-account language bytes
would just read "Python 100%" today. Update LANGUAGES by hand as the
real mix of public work changes.
"""
import sys
from xml.sax.saxutils import escape

LANGUAGES = [
    ("Python", 12, "#3572A5"),
    ("SQL", 25, "#e38c00"),
    ("C#", 20, "#178600"),
    ("JavaScript", 35, "#f1e05a"),
    ("Bash/PowerShell", 8, "#89e051"),
]

WIDTH = 860
PAD_X = 24
PAD_TOP = 24
BAR_H = 14
BAR_RADIUS = 7
LEGEND_ROW_H = 22
LEGEND_COLS = 3
PAD_BOTTOM = 20
BG = "#0d1117"
BORDER = "#30363d"
TEXT_COLOR = "#c9d1d9"
MUTED = "#8b949e"
TITLE_COLOR = "#c9d1d9"

BAR_FILL_DUR = 0.8
BAR_STAGGER = 0.15
LEGEND_START_OFFSET = 0.3


def build_svg() -> str:
    bar_width = WIDTH - PAD_X * 2
    legend_rows = -(-len(LANGUAGES) // LEGEND_COLS)
    height = PAD_TOP + 20 + BAR_H + 18 + legend_rows * LEGEND_ROW_H + PAD_BOTTOM

    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', Menlo, monospace">',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="{PAD_X}" y="{PAD_TOP + 6}" font-size="12" fill="{TITLE_COLOR}" '
        f'font-weight="700">Lenguajes</text>',
        "<defs>",
        f'<clipPath id="barclip"><rect x="{PAD_X}" y="{PAD_TOP + 20}" width="{bar_width}" '
        f'height="{BAR_H}" rx="{BAR_RADIUS}"/></clipPath>',
        "</defs>",
    ]

    bar_y = PAD_TOP + 20
    cursor = PAD_X
    bar_group = [f'<g clip-path="url(#barclip)">']
    for i, (name, pct, color) in enumerate(LANGUAGES):
        seg_width = bar_width * pct / 100
        begin = i * BAR_STAGGER
        bar_group.append(
            f'<rect x="{cursor:.1f}" y="{bar_y}" width="0" height="{BAR_H}" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{seg_width:.1f}" '
            f'dur="{BAR_FILL_DUR}s" begin="{begin:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f"</rect>"
        )
        cursor += seg_width
    bar_group.append("</g>")
    parts.extend(bar_group)

    legend_top = bar_y + BAR_H + 18
    col_width = bar_width / LEGEND_COLS
    for i, (name, pct, color) in enumerate(LANGUAGES):
        col = i % LEGEND_COLS
        row = i // LEGEND_COLS
        x = PAD_X + col * col_width
        y = legend_top + row * LEGEND_ROW_H
        begin = LEGEND_START_OFFSET + i * 0.08
        parts.append(
            f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" '
            f'begin="{begin:.2f}s" fill="freeze"/>'
            f'<rect x="{x:.1f}" y="{y - 10}" width="10" height="10" rx="2" fill="{color}"/>'
            f'<text x="{x + 16:.1f}" y="{y - 1}" font-size="11" fill="{TEXT_COLOR}">'
            f"{escape(name)}</text>"
            f'<text x="{x + col_width - 10:.1f}" y="{y - 1}" font-size="11" fill="{MUTED}" '
            f'text-anchor="end">{pct}%</text>'
            f"</g>"
        )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "language-bar.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print(f"Wrote {out}")
